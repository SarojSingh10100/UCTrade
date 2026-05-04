from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from cart.models import Cart, CartItem
from courses.models import Course, CourseEnrollment
from payments.models import Order, Transaction

User = get_user_model()


class FullCheckoutFlowTests(APITestCase):
    def test_cart_checkout_and_webhook_enrollment(self):
        # create instructor and course
        instructor = User.objects.create_user(username='inst', password='pass1234', is_instructor=True)
        course = Course.objects.create(title='CourseX', description='d', price='10.00', instructor=instructor)

        # create user and add to cart
        user = User.objects.create_user(username='buyer', password='StrongPass')
        token = self.client.post('/api/token/', {'username': 'buyer', 'password': 'StrongPass'}, format='json').data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # add to cart
        add = self.client.post('/api/cart/', {'course': course.id}, format='json')
        self.assertEqual(add.status_code, 201)

        # checkout to create order
        chk = self.client.post('/api/cart/checkout/')
        self.assertEqual(chk.status_code, 201)
        order_id = chk.data['order_id']

        # call create intent (simulated) to create transaction
        pay = self.client.post('/api/payments/create-intent/', {'order_id': order_id}, format='json')
        print('PAY RESPONSE', pay.status_code, pay.data)
        self.assertEqual(pay.status_code, 200)
        txn = Transaction.objects.filter(order_id=order_id).first()
        self.assertIsNotNone(txn)

        # simulate webhook
        evt = {'type': 'payment_intent.succeeded', 'data': {'object': {'id': txn.provider_payment_id}}}
        web = self.client.post('/api/payments/webhook/', evt, format='json')
        self.assertEqual(web.status_code, 200)

        # user should be enrolled
        self.assertTrue(CourseEnrollment.objects.filter(user=user, course=course).exists())
