from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationTests(APITestCase):
    def test_user_registration_and_token_obtain(self):
        url = reverse('register')
        payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPassw0rd!',
            'password2': 'StrongPassw0rd!'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='testuser').exists())

        # obtain token
        token_url = '/api/token/'
        resp = self.client.post(token_url, {'username': 'testuser', 'password': 'StrongPassw0rd!'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access', resp.data)
