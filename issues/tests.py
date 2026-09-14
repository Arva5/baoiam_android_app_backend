from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import IssueReport

User = get_user_model()


class IssueReportAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='rahul@example.com',
            password='password123',
            name='Rahul Sharma',
            email_verified=True,
        )
        self.admin = User.objects.create_user(
            email='admin@baoiam.com',
            password='adminpassword123',
            name='Admin User',
            is_staff=True,
            email_verified=True,
        )
        self.report_url = reverse('issue-report-create')
        self.list_url = reverse('issues-list')

    def test_submit_report_success(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "description": "App crash ho raha hai video play karte waqt"
        }
        res = self.client.post(self.report_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['success'])
        self.assertEqual(res.data['data']['description'], payload['description'])
        self.assertEqual(res.data['data']['status'], 'open')
        self.assertIn('id', res.data['data'])

        # Verify DB
        report = IssueReport.objects.get(pk=res.data['data']['id'])
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.status, 'open')

    def test_submit_report_unauthenticated_fails(self):
        payload = {"description": "App crash ho raha hai"}
        res = self.client.post(self.report_url, payload, format='json')
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_submit_report_blank_description_error(self):
        self.client.force_authenticate(user=self.user)
        payload = {"description": ""}
        res = self.client.post(self.report_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res.data['success'])
        self.assertIn("This field may not be blank.", res.data['errors'])

    def test_list_reports_admin_only(self):
        IssueReport.objects.create(
            user=self.user,
            description="Payment fail ho gaya",
            status="open",
        )

        # Unauthenticated request
        res_unauth = self.client.get(self.list_url)
        self.assertIn(res_unauth.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # Regular user request
        self.client.force_authenticate(user=self.user)
        res_user = self.client.get(self.list_url)
        self.assertEqual(res_user.status_code, status.HTTP_403_FORBIDDEN)

        # Admin user request
        self.client.force_authenticate(user=self.admin)
        res_admin = self.client.get(self.list_url)
        self.assertEqual(res_admin.status_code, status.HTTP_200_OK)
        self.assertTrue(res_admin.data['success'])
        self.assertEqual(len(res_admin.data['data']), 1)
        self.assertEqual(res_admin.data['data'][0]['user_email'], 'rahul@example.com')

    def test_list_reports_filter_by_status_and_email(self):
        user2 = User.objects.create_user(
            email='priya@example.com',
            password='password123',
            name='Priya Patel',
            email_verified=True,
        )
        IssueReport.objects.create(
            user=self.user,
            description="Issue 1",
            status="open",
        )
        IssueReport.objects.create(
            user=user2,
            description="Issue 2",
            status="resolved",
        )

        self.client.force_authenticate(user=self.admin)

        # Filter by status=open
        res_status = self.client.get(self.list_url, {'status': 'open'})
        self.assertEqual(res_status.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_status.data['data']), 1)
        self.assertEqual(res_status.data['data'][0]['status'], 'open')

        # Filter by user_email=priya@example.com
        res_email = self.client.get(self.list_url, {'user_email': 'priya@example.com'})
        self.assertEqual(res_email.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_email.data['data']), 1)
        self.assertEqual(res_email.data['data'][0]['user_email'], 'priya@example.com')
