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
        self.login_url = reverse('login')
        self.me_url = reverse('current_user')
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
