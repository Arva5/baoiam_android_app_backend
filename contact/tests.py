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

    def test_get_contact_messages_list_and_filtering(self):
        # Create 2 messages
        msg1 = ContactMessage.objects.create(
            name='Alice',
            email='alice@example.com',
            subject='Course question',
            message='Tell me about React course.',
            status='pending',
        )
        msg2 = ContactMessage.objects.create(
            name='Bob',
            email='bob@example.com',
            subject='Payment failed',
            message='Payment error on card.',
            status='resolved',
        )

        messages_url = reverse('contact-messages-list')
        response = self.client.get(messages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

        # Filter by status=resolved
        res_filter = self.client.get(messages_url, {'status': 'resolved'})
        self.assertEqual(res_filter.status_code, status.HTTP_200_OK)
        self.assertEqual(res_filter.data['count'], 1)
        self.assertEqual(res_filter.data['data'][0]['name'], 'Bob')

        # Filter by email
        email_filter = self.client.get(messages_url, {'email': 'alice@example.com'})
        self.assertEqual(email_filter.status_code, status.HTTP_200_OK)
        self.assertEqual(email_filter.data['count'], 1)
        self.assertEqual(email_filter.data['data'][0]['name'], 'Alice')

        # Filter by search
        search_filter = self.client.get(messages_url, {'search': 'React'})
        self.assertEqual(search_filter.status_code, status.HTTP_200_OK)
        self.assertEqual(search_filter.data['count'], 1)

    def test_contact_message_detail_and_patch_status(self):
        msg = ContactMessage.objects.create(
            name='Charlie',
            email='charlie@example.com',
            subject='Login trouble',
            message='Unable to login.',
            status='pending',
        )
        detail_url = reverse('contact-messages-detail', kwargs={'pk': msg.id})

        # GET detail
        res = self.client.get(detail_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data']['name'], 'Charlie')

        # PATCH update status to in_progress with admin_notes
        patch_res = self.client.patch(
            detail_url,
            {'status': 'in_progress', 'admin_notes': 'Called customer, investigating.'},
            format='json',
        )
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data['data']['status'], 'in_progress')
        self.assertEqual(patch_res.data['data']['admin_notes'], 'Called customer, investigating.')

        # Verify in DB
        msg.refresh_from_db()
        self.assertEqual(msg.status, 'in_progress')

    def test_get_my_contact_messages(self):
        # Create message for self.user
        ContactMessage.objects.create(
            user=self.user,
            name='Test User',
            email=self.user.email,
            subject='My Inquiry',
            message='Hello, this is my inquiry.',
            status='pending',
        )
        # Create message for someone else
        ContactMessage.objects.create(
            name='Other',
            email='other@example.com',
            subject='Other Inquiry',
            message='Other message.',
            status='pending',
        )

        my_url = reverse('contact-messages-my')

        # Authenticated user
        self.client.force_authenticate(user=self.user)
        res = self.client.get(my_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['data'][0]['subject'], 'My Inquiry')

        # Guest with email query param
        self.client.force_authenticate(user=None)
        guest_res = self.client.get(my_url, {'email': 'other@example.com'})
        self.assertEqual(guest_res.status_code, status.HTTP_200_OK)
        self.assertEqual(guest_res.data['count'], 1)
        self.assertEqual(guest_res.data['data'][0]['name'], 'Other')
