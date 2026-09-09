from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationAPITests(APITestCase):
    def setUp(self):
        self.signup_url = reverse('signup')
        self.verify_email_url = reverse('verify_email')
        self.resend_otp_url = reverse('resend_otp')
        self.login_url = reverse('login')
        self.me_url = reverse('current_user')
        self.profile_url = reverse('user_profile')
        self.delete_account_url = reverse('delete_account')

        self.forgot_password_url = reverse('forgot_password')
        self.reset_password_url = reverse('reset_password')


        self.user_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!'
        }
        self.user = User.objects.create_user(
            name='Jane Doe',
            email='jane@example.com',
            password='JanePassword123!',
            email_verified=True
        )

    def test_signup_success_and_generates_otp(self):
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], self.user_data['email'])
        self.assertEqual(response.data['name'], self.user_data['name'])
        self.assertNotIn('password', response.data)

        user = User.objects.get(email=self.user_data['email'])
        self.assertFalse(user.email_verified)
        self.assertIsNotNone(user.email_otp)
        self.assertEqual(len(user.email_otp), 6)
        self.assertIsNotNone(user.email_otp_expires_at)
        self.assertTrue(user.email_otp_expires_at > timezone.now())

    def test_signup_password_mismatch(self):
        data = self.user_data.copy()
        data['confirm_password'] = 'DifferentPassword123!'
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)

    def test_signup_duplicate_email(self):
        data = self.user_data.copy()
        data['email'] = 'jane@example.com'
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_email_success(self):
        # Create unverified user with OTP
        unverified_user = User.objects.create_user(
            name='Unverified User',
            email='unverified@example.com',
            password='Password123!',
            email_verified=False,
            email_otp='654321',
            email_otp_expires_at=timezone.now() + timedelta(minutes=10)
        )

        response = self.client.post(self.verify_email_url, {
            'email': 'unverified@example.com',
            'otp': '654321'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Email verified successfully.')

        unverified_user.refresh_from_db()
        self.assertTrue(unverified_user.email_verified)
        self.assertIsNone(unverified_user.email_otp)
        self.assertIsNone(unverified_user.email_otp_expires_at)

    def test_verify_email_invalid_otp(self):
        User.objects.create_user(
            name='Unverified User 2',
            email='unverified2@example.com',
            password='Password123!',
            email_verified=False,
            email_otp='112233',
            email_otp_expires_at=timezone.now() + timedelta(minutes=10)
        )

        response = self.client.post(self.verify_email_url, {
            'email': 'unverified2@example.com',
            'otp': '999999'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_email_expired_otp(self):
        User.objects.create_user(
            name='Unverified User 3',
            email='unverified3@example.com',
            password='Password123!',
            email_verified=False,
            email_otp='123456',
            email_otp_expires_at=timezone.now() - timedelta(minutes=1)
        )

        response = self.client.post(self.verify_email_url, {
            'email': 'unverified3@example.com',
            'otp': '123456'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success_when_verified(self):
        payload = {
            'email': 'jane@example.com',
            'password': 'JanePassword123!',
            'remember_me': False
        }
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_fails_when_email_not_verified(self):
        User.objects.create_user(
            name='Not Verified',
            email='notverified@example.com',
            password='Password123!',
            email_verified=False
        )

        payload = {
            'email': 'notverified@example.com',
            'password': 'Password123!'
        }
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['non_field_errors'][0],
            "Please verify your email before logging in."
        )

    def test_login_remember_me(self):
        payload = {
            'email': 'jane@example.com',
            'password': 'JanePassword123!',
            'remember_me': True
        }
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        payload = {
            'email': 'jane@example.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_current_user_authenticated(self):
        login_res = self.client.post(self.login_url, {
            'email': 'jane@example.com',
            'password': 'JanePassword123!'
        })
        access_token = login_res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['name'], self.user.name)
        self.assertEqual(response.data['email'], self.user.email)

    def test_current_user_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forgot_password_generates_token(self):
        response = self.client.post(self.forgot_password_url, {'email': 'jane@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.reset_password_token)
        self.assertIsNotNone(self.user.reset_password_token_expires_at)

    def test_forgot_password_nonexistent_email_generic_response(self):
        response = self.client.post(self.forgot_password_url, {'email': 'unknown@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_success(self):
        # Generate token
        self.client.post(self.forgot_password_url, {'email': 'jane@example.com'})
        self.user.refresh_from_db()
        token = self.user.reset_password_token

        payload = {
            'reset_token': token,
            'new_password': 'BrandNewPassword123!',
            'confirm_password': 'BrandNewPassword123!'
        }
        response = self.client.post(self.reset_password_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Invalidate token check
        self.user.refresh_from_db()
        self.assertIsNone(self.user.reset_password_token)
        self.assertIsNone(self.user.reset_password_token_expires_at)

        # Verify new password login works
        login_res = self.client.post(self.login_url, {
            'email': 'jane@example.com',
            'password': 'BrandNewPassword123!'
        })
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)

    def test_reset_password_expired_token(self):
        self.user.reset_password_token = 'expired_token'
        self.user.reset_password_token_expires_at = timezone.now() - timedelta(minutes=10)
        self.user.save()

        payload = {
            'reset_token': 'expired_token',
            'new_password': 'BrandNewPassword123!',
            'confirm_password': 'BrandNewPassword123!'
        }
        response = self.client.post(self.reset_password_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resend_otp_success_and_sends_email(self):
        mail.outbox.clear()
        unverified_user = User.objects.create_user(
            name='Test Unverified',
            email='unverified_resend@example.com',
            password='Password123!',
            email_verified=False,
            email_otp='111111',
            email_otp_expires_at=timezone.now() + timedelta(minutes=5),
            email_otp_last_sent_at=timezone.now() - timedelta(seconds=70)
        )

        response = self.client.post(self.resend_otp_url, {'email': 'unverified_resend@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        unverified_user.refresh_from_db()
        self.assertNotEqual(unverified_user.email_otp, '111111')
        self.assertEqual(len(unverified_user.email_otp), 6)
        self.assertTrue(unverified_user.email_otp_expires_at > timezone.now())

        # Verify email was dispatched
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject, 'Verify Your Email - OTP')
        self.assertIn(unverified_user.name, sent_mail.body)
        self.assertIn(unverified_user.email_otp, sent_mail.body)
        self.assertEqual(sent_mail.to, ['unverified_resend@example.com'])

    def test_resend_otp_already_verified(self):
        response = self.client.post(self.resend_otp_url, {'email': 'jane@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Email is already verified.')

    def test_resend_otp_rate_limited(self):
        unverified_user = User.objects.create_user(
            name='Rate Limited',
            email='ratelimited@example.com',
            password='Password123!',
            email_verified=False,
            email_otp='222222',
            email_otp_expires_at=timezone.now() + timedelta(minutes=10),
            email_otp_last_sent_at=timezone.now() - timedelta(seconds=20)
        )

        response = self.client.post(self.resend_otp_url, {'email': 'ratelimited@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Please wait', response.data['detail'])

    def test_resend_otp_nonexistent_email_generic_response(self):
        mail.outbox.clear()
        response = self.client.post(self.resend_otp_url, {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)

    def test_delete_account_success(self):
        login_res = self.client.post(self.login_url, {
            'email': 'jane@example.com',
            'password': 'JanePassword123!'
        })
        access_token = login_res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.delete(self.delete_account_url, {'password': 'JanePassword123!'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Account deleted successfully.')
        self.assertFalse(User.objects.filter(email='jane@example.com').exists())

    def test_delete_account_incorrect_password(self):
        login_res = self.client.post(self.login_url, {
            'email': 'jane@example.com',
            'password': 'JanePassword123!'
        })
        access_token = login_res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.delete(self.delete_account_url, {'password': 'WrongPassword123!'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Incorrect password.')
        self.assertTrue(User.objects.filter(email='jane@example.com').exists())

    def test_delete_account_unauthenticated(self):
        response = self.client.delete(self.delete_account_url, {'password': 'JanePassword123!'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_auto_creates_and_returns_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_email'], 'jane@example.com')
        self.assertEqual(response.data['user_name'], 'Jane Doe')
        self.assertFalse(response.data['is_profile_completed'])

    def test_patch_profile_updates_allowed_fields(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'avatar_url': 'https://example.com/avatar.jpg',
            'headline': 'Full Stack Developer',
            'bio': 'Passionate about coding.',
            'phone_number': '+1234567890',
            'target_role': 'Software Engineer',
            'interests': ['Web Development', 'AI'],
            'skills': ['Python', 'Django', 'React'],
            'is_profile_completed': True,
        }
        response = self.client.patch(self.profile_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['headline'], 'Full Stack Developer')
        self.assertEqual(response.data['target_role'], 'Software Engineer')
        self.assertEqual(response.data['interests'], ['Web Development', 'AI'])
        self.assertEqual(response.data['skills'], ['Python', 'Django', 'React'])
        self.assertTrue(response.data['is_profile_completed'])

    def test_get_profile_includes_education_skills_and_contact_defaults(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['highest_qualification'], '')
        self.assertEqual(response.data['institution'], '')
        self.assertEqual(response.data['field_of_study'], '')
        self.assertEqual(response.data['skills'], [])
        self.assertEqual(response.data['phone_number'], '')
        self.assertEqual(response.data['linkedin_url'], '')
        self.assertEqual(response.data['github_url'], '')
        self.assertEqual(response.data['website_url'], '')

    def test_patch_profile_educational_background(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'highest_qualification': 'B.Tech',
            'institution': 'IIT Delhi',
            'field_of_study': 'Computer Science',
        }
        response = self.client.patch(self.profile_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['highest_qualification'], 'B.Tech')
        self.assertEqual(response.data['institution'], 'IIT Delhi')
        self.assertEqual(response.data['field_of_study'], 'Computer Science')
        profile = self.user.profile
        profile.refresh_from_db()
        self.assertEqual(profile.institution, 'IIT Delhi')

    def test_patch_profile_contact_information(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'phone_number': '+919876543210',
            'linkedin_url': 'https://linkedin.com/in/jane',
            'github_url': 'https://github.com/jane',
            'website_url': 'https://jane.dev',
        }
        response = self.client.patch(self.profile_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '+919876543210')
        self.assertEqual(response.data['linkedin_url'], 'https://linkedin.com/in/jane')
        self.assertEqual(response.data['github_url'], 'https://github.com/jane')
        self.assertEqual(response.data['website_url'], 'https://jane.dev')
        self.assertEqual(response.data['user_email'], 'jane@example.com')

    def test_patch_profile_rejects_invalid_skills(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.profile_url, {'skills': 'Python'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('skills', response.data)

    def test_patch_profile_does_not_change_email_or_auth(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'user_email': 'hacker@example.com',
            'email': 'hacker@example.com',
            'password': 'HackedPassword123!',
            'headline': 'Security Researcher',
        }
        response = self.client.patch(self.profile_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'jane@example.com')
        self.assertTrue(self.user.check_password('JanePassword123!'))

    def test_profile_unauthenticated(self):
        res_get = self.client.get(self.profile_url)
        self.assertEqual(res_get.status_code, status.HTTP_401_UNAUTHORIZED)
        res_patch = self.client.patch(self.profile_url, {'headline': 'Test'})
        self.assertEqual(res_patch.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfilePreferencesAPITests(APITestCase):
    def setUp(self):
        self.profile_url = reverse('user_profile')
        self.setup_url = reverse('profile_setup')
        self.user = User.objects.create_user(
            name='Jane Doe',
            email='jane@example.com',
            password='JanePassword123!',
            email_verified=True,
        )

    def test_get_profile_preference_defaults(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['language'], 'en')
        self.assertTrue(response.data['notifications_enabled'])
        self.assertEqual(response.data['timezone'], 'Asia/Kolkata')

    def test_patch_profile_updates_preferences(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'language': 'hi',
            'notifications_enabled': False,
            'timezone': 'America/New_York',
        }
        response = self.client.patch(self.profile_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['language'], 'hi')
        self.assertFalse(response.data['notifications_enabled'])
        self.assertEqual(response.data['timezone'], 'America/New_York')
        profile = self.user.profile
        profile.refresh_from_db()
        self.assertEqual(profile.language, 'hi')
        self.assertFalse(profile.notifications_enabled)
        self.assertEqual(profile.timezone, 'America/New_York')

    def test_patch_profile_setup_updates_preferences(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.setup_url,
            {'language': 'en', 'timezone': 'Asia/Kolkata'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['language'], 'en')
        self.assertEqual(response.data['data']['timezone'], 'Asia/Kolkata')

    def test_patch_normalizes_language_code(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.profile_url, {'language': 'EN-us'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['language'], 'en-US')

    def test_patch_rejects_invalid_language(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.profile_url, {'language': 'english'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('language', response.data)

    def test_patch_rejects_invalid_timezone(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.profile_url, {'timezone': 'Kolkata'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('timezone', response.data)

    def test_preferences_unauthenticated(self):
        res_get = self.client.get(self.profile_url)
        self.assertEqual(res_get.status_code, status.HTTP_401_UNAUTHORIZED)
        res_patch = self.client.patch(
            self.profile_url,
            {'language': 'hi', 'notifications_enabled': False},
            format='json',
        )
        self.assertEqual(res_patch.status_code, status.HTTP_401_UNAUTHORIZED)


class PersonalInfoAPITests(APITestCase):
    def setUp(self):
        from rest_framework_simplejwt.tokens import RefreshToken
        self.url = reverse('personal_info')
        self.user = User.objects.create_user(
            name='Alice',
            email='alice@example.com',
            password='AlicePass123!',
            email_verified=True,
        )
        self.other_user = User.objects.create_user(
            name='Bob',
            email='bob@example.com',
            password='BobPass123!',
            email_verified=True,
            username='bob_unique',
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    # --- Auth guard ---
    def test_get_requires_authentication(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_requires_authentication(self):
        self.client.credentials()
        response = self.client.patch(self.url, {'full_name': 'Alice Smith'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- GET ---
    def test_get_returns_personal_info_fields(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ('full_name', 'username', 'professional_headline'):
            self.assertIn(field, response.data)

    def test_get_returns_only_own_data(self):
        self.user.full_name = 'Alice Smith'
        self.user.username = 'alice_s'
        self.user.professional_headline = 'Mobile Dev'
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.data['full_name'], 'Alice Smith')
        self.assertEqual(response.data['username'], 'alice_s')
        self.assertEqual(response.data['professional_headline'], 'Mobile Dev')

    # --- PATCH ---
    def test_patch_updates_fields(self):
        payload = {
            'full_name': 'Alice Smith',
            'username': 'alice_smith',
            'professional_headline': 'Senior Android Engineer',
        }
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, 'Alice Smith')
        self.assertEqual(self.user.username, 'alice_smith')
        self.assertEqual(self.user.professional_headline, 'Senior Android Engineer')

    def test_patch_is_partial(self):
        self.user.full_name = 'Alice'
        self.user.save()
        response = self.client.patch(self.url, {'professional_headline': 'Dev'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, 'Alice')  # unchanged

    # --- Username uniqueness ---
    def test_duplicate_username_is_rejected(self):
        response = self.client.patch(self.url, {'username': 'bob_unique'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_username_uniqueness_is_case_insensitive(self):
        response = self.client.patch(self.url, {'username': 'BOB_UNIQUE'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_updating_own_username_to_same_value_is_allowed(self):
        self.user.username = 'alice_own'
        self.user.save()
        response = self.client.patch(self.url, {'username': 'alice_own'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TwitterUrlProfileTests(APITestCase):
    """Tests for twitter_url field on UserProfile."""

    def setUp(self):
        self.profile_url = reverse('user_profile')
        self.setup_url = reverse('profile_setup')
        self.user = User.objects.create_user(
            name='Twitter Tester',
            email='twitter@example.com',
            password='TestPass123!',
            email_verified=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_twitter_url_default_is_empty_string(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('twitter_url', response.data)
        self.assertEqual(response.data['twitter_url'], '')

    def test_patch_profile_updates_twitter_url(self):
        payload = {'twitter_url': 'https://twitter.com/twittertester'}
        response = self.client.patch(self.profile_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['twitter_url'], 'https://twitter.com/twittertester')
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.twitter_url, 'https://twitter.com/twittertester')

    def test_patch_profile_setup_updates_twitter_url(self):
        payload = {'twitter_url': 'https://x.com/twittertester'}
        response = self.client.patch(self.setup_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['twitter_url'], 'https://x.com/twittertester')
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.twitter_url, 'https://x.com/twittertester')

    def test_patch_profile_clears_twitter_url(self):
        # Set a value first via the API (profile is auto-created on first request)
        self.client.patch(
            self.profile_url,
            {'twitter_url': 'https://twitter.com/old'},
            format='json',
        )
        # Now clear it
        response = self.client.patch(self.profile_url, {'twitter_url': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['twitter_url'], '')

    def test_existing_contact_fields_still_present_alongside_twitter(self):
        """Ensure twitter_url addition doesn't break linkedin/github/website fields."""
        payload = {
            'linkedin_url': 'https://linkedin.com/in/tester',
            'github_url': 'https://github.com/tester',
            'website_url': 'https://tester.dev',
            'twitter_url': 'https://twitter.com/tester',
        }
        response = self.client.patch(self.profile_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['linkedin_url'], 'https://linkedin.com/in/tester')
        self.assertEqual(response.data['github_url'], 'https://github.com/tester')
        self.assertEqual(response.data['website_url'], 'https://tester.dev')
        self.assertEqual(response.data['twitter_url'], 'https://twitter.com/tester')

