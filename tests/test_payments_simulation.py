from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from payments.models import Order, Transaction

User = get_user_model()


class StripeSimulationTests(APITestCase):
    def test_create_payment_intent_simulation_and_webhook(self):
        user = User.objects.create_user(username='payuser', password='StrongPassw0rd!')
        # obtain token
        token_resp = self.client.post('/api/token/', {'username': 'payuser', 'password': 'StrongPassw0rd!'}, format='json')
        self.assertEqual(token_resp.status_code, 200)
        access = token_resp.data['access']

        # create order
        order = Order.objects.create(user=user, total_amount='19.99', paid=False)

        # call create-intent (no STRIPE_SECRET_KEY configured in tests) -> should return simulated client_secret
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        resp = self.client.post('/api/payments/create-intent/', {'order_id': order.id}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('client_secret', resp.data)
        client_secret = resp.data['client_secret']
        self.assertTrue(client_secret.startswith('test_cs_'))

        # there should be a Transaction created with provider_payment_id 'test_pi_{order.id}' and pending status
        txn = Transaction.objects.filter(order=order).first()
        self.assertIsNotNone(txn)
        self.assertTrue(txn.provider_payment_id.startswith('test_pi_'))
        self.assertEqual(txn.status, 'pending')

        # simulate webhook (payment_intent.succeeded)
        event = {
            'type': 'payment_intent.succeeded',
            'data': {'object': {'id': txn.provider_payment_id}}
        }
        web_resp = self.client.post('/api/payments/webhook/', event, format='json')
        self.assertEqual(web_resp.status_code, 200)

        txn.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(txn.status, 'succeeded')
        self.assertTrue(order.paid)
