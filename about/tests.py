from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from about.models import AboutOverview, ImpactStat, WhyChooseUsItem, SuccessStory, TeamMember
from contact.models import ContactMessage

User = get_user_model()


class AboutUsApiTests(APITestCase):
    def setUp(self):
        # Create normal user
        self.normal_user = User.objects.create_user(
            email='student@example.com',
            password='password123',
            name='Student User',
        )

        # Create admin/staff user
        self.admin_user = User.objects.create_user(
            email='admin@baoiam.com',
            password='adminpassword123',
            name='Admin User',
            is_staff=True,
        )

        # Setup initial models
        self.overview = AboutOverview.objects.create(
            title="About BAOIAM",
            mission_text="Empowering learners worldwide.",
            trusted_by_labels=["TechCorp", "EduPlus"],
        )
        self.stat = ImpactStat.objects.create(
            value="1M+",
            label="Students",
            icon="Groups",
            display_order=1,
            is_active=True,
        )
        self.offer = WhyChooseUsItem.objects.create(
            title="Live Classes",
            description="Interactive experience",
            icon="VideoCall",
            display_order=1,
            is_active=True,
        )
        self.story = SuccessStory.objects.create(
            name="Peter Jones",
            role="Alumni",
            rating=5,
            story="Amazing program!",
            display_order=1,
            is_active=True,
        )
        self.team = TeamMember.objects.create(
            name="James Perkins",
            role="CEO",
            display_order=1,
            is_active=True,
        )

    def test_get_about_us_screen_data_public(self):
        """Main endpoint for Android Dev: GET /api/about-us/"""
        response = self.client.get('/api/about-us/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        data = response.data['data']

        # Check camelCase fields for Kotlin AboutUsUiState
        self.assertIn('missionText', data)
        self.assertIn('impactStats', data)
        self.assertIn('whatWeOffer', data)
        self.assertIn('successStories', data)
        self.assertIn('teamMembers', data)
        self.assertIn('trustedByLabels', data)

        self.assertEqual(len(data['impactStats']), 1)
        self.assertEqual(data['impactStats'][0]['value'], '1M+')
        self.assertEqual(data['impactStats'][0]['icon'], 'Groups')

    def test_get_about_us_screen_data_alias(self):
        """Alias route GET /api/about/ works identically"""
        response = self.client.get('/api/about/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_user_submit_success_story(self):
        """Learner can submit story, saved with is_active=False"""
        payload = {
            "name": "Aarav Sharma",
            "role": "Data Scientist",
            "rating": 5,
            "story": "I loved the live hands-on projects and mentoring support.",
        }
        response = self.client.post('/api/about-us/stories/submit/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])

        # Verify in DB that it is pending approval (is_active=False)
        created_story = SuccessStory.objects.get(name="Aarav Sharma")
        self.assertFalse(created_story.is_active)

    def test_impact_stats_crud_permissions(self):
        """Admin only can create/update/delete impact stats"""
        new_stat_payload = {
            "value": "200+",
            "label": "Mentors",
            "icon": "School",
            "display_order": 5,
        }

        # Unauthenticated POST should fail
        res = self.client.post('/api/about-us/stats/', new_stat_payload, format='json')
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # Admin user authenticated POST should succeed
        self.client.force_authenticate(user=self.admin_user)
        res_admin = self.client.post('/api/about-us/stats/', new_stat_payload, format='json')
        self.assertEqual(res_admin.status_code, status.HTTP_201_CREATED)
        new_id = res_admin.data['data']['id']

        # PATCH stat
        patch_res = self.client.patch(f'/api/about-us/stats/{new_id}/', {"value": "250+"}, format='json')
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data['data']['value'], "250+")

        # DELETE stat
        del_res = self.client.delete(f'/api/about-us/stats/{new_id}/')
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertFalse(ImpactStat.objects.filter(pk=new_id).exists())

    def test_update_overview_admin(self):
        """Admin can update mission text and trusted brands"""
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            "mission_text": "Updated company mission text.",
            "trusted_by_labels": ["Google", "Microsoft", "Amazon"],
        }
        res = self.client.put('/api/about-us/overview/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data']['mission_text'], "Updated company mission text.")


class ContactUsPermissionFixTests(APITestCase):
    def setUp(self):
        self.normal_user = User.objects.create_user(
            email='student@example.com',
            password='password123',
            name='Student User',
        )
        self.admin_user = User.objects.create_user(
            email='admin@baoiam.com',
            password='adminpassword123',
            name='Admin User',
            is_staff=True,
        )
        self.msg = ContactMessage.objects.create(
            name="Riya",
            email="riya@example.com",
            subject="Billing issue",
            message="Payment deducted twice.",
            status="pending",
        )

    def test_get_all_contact_messages_forbidden_for_public_and_normal_user(self):
        """Normal/guest user cannot view all contact messages"""
        res_guest = self.client.get('/api/contact/messages/')
        self.assertIn(res_guest.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        self.client.force_authenticate(user=self.normal_user)
        res_normal = self.client.get('/api/contact/messages/')
        self.assertEqual(res_normal.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_contact_messages_allowed_for_admin(self):
        """Admin can view all contact messages"""
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get('/api/contact/messages/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])
        self.assertGreaterEqual(res.data['count'], 1)

    def test_contact_message_patch_allowed_for_admin_only(self):
        """Admin can update status of contact message"""
        self.client.force_authenticate(user=self.normal_user)
        res = self.client.patch(f'/api/contact/messages/{self.msg.id}/', {"status": "resolved"}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin_user)
        res_admin = self.client.patch(
            f'/api/contact/messages/{self.msg.id}/',
            {"status": "resolved", "admin_notes": "Refund approved"},
            format='json',
        )
        self.assertEqual(res_admin.status_code, status.HTTP_200_OK)
        self.assertEqual(res_admin.data['data']['status'], "resolved")
