from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ContactMessage, ContactSupportChannel, PopularQuestion

User = get_user_model()


class ContactApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='TestPassword123!',
            email_verified=True,
        )

        self.channel = ContactSupportChannel.objects.create(
            channel_type='live_chat',
            title='Live Chat',
            subtitle='2 min response',
            value='https://chat.example.com',
            is_active=True,
            display_order=1,
        )

        self.question = PopularQuestion.objects.create(
            question='How to reset password?',
            answer='Click forgot password on login screen.',
            category='Account',
            is_active=True,
            display_order=1,
        )

        self.screen_url = reverse('contact-screen')
        self.message_url = reverse('contact-message-create')
        self.questions_url = reverse('popular-questions-list')

    def test_get_contact_screen_info(self):
        response = self.client.get(self.screen_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))
        data = response.data.get('data', {})
        self.assertEqual(data.get('title'), 'Contact Us')
        self.assertIn('channels', data)
        self.assertIn('subject_options', data)
        self.assertIn('popular_questions', data)
        self.assertIn('support_badge', data)
        self.assertEqual(len(data['channels']), 1)
        self.assertEqual(data['channels'][0]['title'], 'Live Chat')

    def test_post_contact_message_as_guest(self):
        payload = {
            'name': 'Guest John',
            'email': 'guest.john@example.com',
            'subject': 'Course Inquiry',
            'message': 'I would like to know more about the Android Bootcamp.',
        }
        response = self.client.post(self.message_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get('success'))
        msg_id = response.data['data']['id']
        message = ContactMessage.objects.get(id=msg_id)
        self.assertEqual(message.name, 'Guest John')
        self.assertEqual(message.email, 'guest.john@example.com')
        self.assertIsNone(message.user)
        self.assertEqual(message.status, 'pending')

    def test_post_contact_message_as_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'name': 'Test User',
            'email': 'testuser@example.com',
            'subject': 'Payment Issue',
            'message': 'My payment was deducted but enrollment is pending.',
        }
        response = self.client.post(self.message_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get('success'))
        msg_id = response.data['data']['id']
        message = ContactMessage.objects.get(id=msg_id)
        self.assertEqual(message.user, self.user)

    def test_post_contact_message_validation_failure(self):
        # Missing required fields
        payload = {
            'name': '',
            'email': 'invalid-email-address',
            'subject': '',
            'message': '',
        }
        response = self.client.post(self.message_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get('success'))
        self.assertIn('errors', response.data)
        errors = response.data['errors']
        self.assertIn('email', errors)
        self.assertIn('name', errors)
        self.assertIn('subject', errors)
        self.assertIn('message', errors)

    def test_get_popular_questions_list_and_detail(self):
        response = self.client.get(self.questions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))
        self.assertEqual(len(response.data.get('data')), 1)

        detail_url = reverse('popular-question-detail', kwargs={'pk': self.question.id})
        detail_resp = self.client.get(detail_url)
        self.assertEqual(detail_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_resp.data['data']['question'], 'How to reset password?')
