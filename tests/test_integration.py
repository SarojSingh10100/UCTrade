from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course

User = get_user_model()


class IntegrationTests(APITestCase):
    def test_register_token_create_course_and_cart(self):
        # register user
        resp = self.client.post(reverse('register'), {
            'username': 'inst', 'email': 'inst@example.com', 'password': 'StrongPassw0rd!', 'password2': 'StrongPassw0rd!', 'is_instructor': True
        }, format='json')
        self.assertEqual(resp.status_code, 201)

        # obtain token
        token_resp = self.client.post('/api/token/', {'username': 'inst', 'password': 'StrongPassw0rd!'}, format='json')
        self.assertEqual(token_resp.status_code, 200)
        access = token_resp.data['access']

        # create course
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        cr = self.client.post('/api/courses/', {'title': 'CI Course', 'description': 'desc', 'price': '9.99'}, format='json')
        self.assertEqual(cr.status_code, 201)
        course_id = cr.data['id']

        # add to cart
        cart_resp = self.client.post('/api/cart/', {'course': course_id}, format='json')
        self.assertEqual(cart_resp.status_code, 201)
        self.assertEqual(cart_resp.data['course'], course_id)
