from django.core import mail
from django.test import override_settings
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from classes.models import ClassSession

User = get_user_model()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class NotificationCeleryTests(APITestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(username='inst', password='pass1234', is_instructor=True, email='inst@example.com')
        self.user = User.objects.create_user(username='student', password='pass1234', email='student@example.com')

    def test_enroll_schedules_notification_and_sends_email(self):
        # instructor creates class
        token = self.client.post('/api/token/', {'username': 'inst', 'password': 'pass1234'}, format='json').data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        course = {'title': 'C1', 'description': 'd', 'price': '0'}
        cr = self.client.post('/api/courses/', course, format='json')
        course_id = cr.data['id']
        cls_resp = self.client.post('/api/classes/', {'course': course_id, 'title': 'S1', 'start_time': '2030-01-01T10:00:00Z', 'end_time': '2030-01-01T11:00:00Z'}, format='json')
        self.assertEqual(cls_resp.status_code, 201)
        cls_id = cls_resp.data['id']

        # student enrolls
        token_student = self.client.post('/api/token/', {'username': 'student', 'password': 'pass1234'}, format='json').data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_student}')
        enroll_resp = self.client.post(f'/api/classes/{cls_id}/enroll/')
        self.assertEqual(enroll_resp.status_code, 201)

        # because CELERY_TASK_ALWAYS_EAGER=True in settings by default for dev, the task runs synchronously
        # check notifications and outgoing email
        notes = self.client.get('/api/notifications/')
        self.assertEqual(notes.status_code, 200)
        self.assertTrue(len(notes.data) >= 1)

        # check email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('Enrolled:', email.subject)
        self.assertIn('You have been enrolled', email.body)
