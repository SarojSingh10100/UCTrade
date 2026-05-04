from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course, PDFMaterial
from videos.models import Video
from payments.models import Order, Transaction

User = get_user_model()


class FileUploadsAndNotificationTests(APITestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(username='inst', password='pass1234', is_instructor=True)
        self.user = User.objects.create_user(username='user', password='pass1234')

    def _get_token(self, username, password):
        resp = self.client.post('/api/token/', {'username': username, 'password': password}, format='json')
        return resp.data['access']

    def test_pdf_upload(self):
        access = self._get_token('inst', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        course_resp = self.client.post('/api/courses/', {'title': 'Upload Course', 'description': 'd', 'price': '0'}, format='json')
        self.assertEqual(course_resp.status_code, 201)
        course_id = course_resp.data['id']

        pdf = SimpleUploadedFile('syllabus.pdf', b'%PDF-1.4 file content', content_type='application/pdf')
        resp = self.client.post('/api/courses/materials/', {'course': course_id, 'title': 'Syllabus', 'file': pdf}, format='multipart')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(PDFMaterial.objects.filter(title='Syllabus', course_id=course_id).exists())

    def test_video_upload(self):
        access = self._get_token('inst', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        course_resp = self.client.post('/api/courses/', {'title': 'Video Course', 'description': 'd', 'price': '0'}, format='json')
        course_id = course_resp.data['id']

        video = SimpleUploadedFile('lecture.mp4', b'fake video content', content_type='video/mp4')
        resp = self.client.post('/api/videos/', {'course': course_id, 'title': 'Lecture 1', 'file': video}, format='multipart')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Video.objects.filter(title='Lecture 1', course_id=course_id).exists())

    def test_notifications_and_webhook(self):
        # create notification as instructor
        access = self._get_token('inst', 'pass1234')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        note_resp = self.client.post('/api/notifications/', {'title': 'Note', 'message': 'Hello'}, format='json')
        self.assertEqual(note_resp.status_code, 201)

        # list notifications as instructor
        list_resp = self.client.get('/api/notifications/')
        self.assertEqual(list_resp.status_code, 200)
        self.assertTrue(len(list_resp.data) >= 1)

        # create an order and transaction to simulate Stripe webhook
        order = Order.objects.create(user=self.instructor, total_amount='9.99', paid=False)
        txn = Transaction.objects.create(order=order, provider_payment_id='pi_test_123', amount=order.total_amount, status='pending')

        # simulate webhook event
        event = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_123'
                }
            }
        }
        # no signature header (STRIPE_WEBHOOK_SECRET not configured in tests), should be accepted
        web_resp = self.client.post('/api/payments/webhook/', event, format='json')
        self.assertEqual(web_resp.status_code, 200)

        txn.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(txn.status, 'succeeded')
        self.assertTrue(order.paid)
