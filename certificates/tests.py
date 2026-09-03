from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from certificates.models import Certificate, UserCertificate

User = get_user_model()


class CertificatesAppTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='certuser@example.com',
            name='Certificate Holder',
            password='Password123!',
        )
        self.cert = Certificate.objects.create(
            title='Python Full Stack Certificate',
            issuer_name='Baoiam Platform',
            is_active=True,
        )
        self.user_cert = UserCertificate.objects.create(
            user=self.user,
            certificate=self.cert,
            certificate_code='CERT-PY-2026-999',
            is_verified=True,
        )

    def test_list_certificates(self):
        url = reverse('certificate-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_certificates(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-certificates')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['certificate_code'], 'CERT-PY-2026-999')

    def test_verify_certificate(self):
        url = reverse('verify-certificate', kwargs={'certificate_code': 'CERT-PY-2026-999'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_valid'])
        self.assertEqual(response.data['certificate']['recipient_name'], 'Certificate Holder')
