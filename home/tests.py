from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import UserProfile
from assessments.models import Assessment, Option, Question, UserAssessmentAttempt
from certificates.models import Certificate, UserCertificate
from courses.models import (
    Category,
    Course,
    CourseEnrollment,
    PromotionalBanner,
    TipOfTheDay,
    WhyChooseUsItem,
)

User = get_user_model()


class HomeScreen1EngagementTests(APITestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            email='learner@example.com',
            name='Learner User',
            password='Password123!',
            email_verified=True,
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            headline='Aspiring Android Engineer',
            is_profile_completed=True,
        )

        # Create category and course
        self.category = Category.objects.create(
            name='Mobile Development',
            slug='mobile-development',
        )
        self.course = Course.objects.create(
            title='Android App Development with Kotlin',
            slug='android-kotlin-masterclass',
            category=self.category,
            price=Decimal('49.99'),
            duration_hours=Decimal('24.5'),
            rating=Decimal('4.9'),
            is_featured=True,
            is_published=True,
        )

        # Create enrollment
        self.enrollment = CourseEnrollment.objects.create(
            user=self.user,
            course=self.course,
            progress_percentage=45,
            completed_lessons=9,
            total_lessons=20,
            current_lesson_title='Building UI with Jetpack Compose',
        )

        # Create promotional banner
        self.banner = PromotionalBanner.objects.create(
            title='Summer Tech Fest: 40% Off',
            badge_text='LIMITED OFFER',
            discount_code='SUMMER40',
            discount_percentage=40,
            target_type='course',
            target_id=str(self.course.id),
            order=1,
            is_active=True,
        )

        # Create Tip of the Day
        self.tip = TipOfTheDay.objects.create(
            title='Pomodoro for Coders',
            content='Code intensely for 25 minutes, then take a 5-minute break to stay sharp.',
            category='Focus & Productivity',
            publish_date=timezone.localdate(),
            is_active=True,
        )

        # Create Why Choose Us Item
        self.why_us = WhyChooseUsItem.objects.create(
            title='Hands-on Real World Projects',
            description='Build 10+ production-ready apps to showcase in your portfolio.',
            highlight_stat='10+ Live Projects',
            order=1,
            is_active=True,
        )

        # Create Assessment (Learning Path Quiz)
        self.quiz = Assessment.objects.create(
            title='Tech Career Path Finder',
            subtitle='Find the ideal track suited for your aspirations',
            quiz_type='career_path',
            estimated_minutes=3,
            is_featured=True,
            is_active=True,
        )
        self.question = Question.objects.create(
            assessment=self.quiz,
            question_text='What kind of projects excite you the most?',
            order=1,
        )
        self.opt1 = Option.objects.create(
            question=self.question,
            option_text='Mobile Apps & UI',
            career_track='Mobile Development',
            order=1,
        )
        self.opt2 = Option.objects.create(
            question=self.question,
            option_text='AI & Data Analytics',
            career_track='Data Science',
            order=2,
        )

        # Create Certificate
        self.certificate = Certificate.objects.create(
            title='Certified Android Specialist',
            course=self.course,
            issuer_name='Baoiam Education',
        )
        self.user_cert = UserCertificate.objects.create(
            user=self.user,
            certificate=self.certificate,
            certificate_code='BAO-AND-2026-001',
            is_verified=True,
        )

    def test_aggregated_home_screen_1_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('home-engagement')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # Check all 6 engagement sections exist
        self.assertIn('getting_started', data)
        self.assertIn('promotional_banners', data)
        self.assertIn('learning_path_quiz', data)
        self.assertIn('why_choose_us', data)
        self.assertIn('tip_of_the_day', data)
        self.assertIn('start_your_journey', data)

        # 1. Getting Started verification
        getting_started = data['getting_started']
        self.assertEqual(len(getting_started['steps']), 3)
        self.assertTrue(getting_started['steps'][0]['is_completed'])  # profile
        self.assertTrue(getting_started['steps'][1]['is_completed'])  # enrollment
        self.assertTrue(getting_started['steps'][2]['is_completed'])  # learning start (progress > 0)
        self.assertEqual(getting_started['progress_percentage'], 100)
        self.assertTrue(getting_started['is_completed'])

        # 2. Promotional Banner verification
        banners = data['promotional_banners']
        self.assertEqual(len(banners), 1)
        self.assertEqual(banners[0]['discount_code'], 'SUMMER40')

        # 3. Learning Path Quiz verification
        quiz_data = data['learning_path_quiz']
        self.assertTrue(quiz_data['is_available'])
        self.assertEqual(quiz_data['quiz']['title'], 'Tech Career Path Finder')

        # 4. Why Choose Us verification
        why_us_data = data['why_choose_us']
        self.assertEqual(len(why_us_data['items']), 1)
        self.assertEqual(why_us_data['items'][0]['title'], 'Hands-on Real World Projects')

        # 5. Tip of the Day verification
        tip_data = data['tip_of_the_day']
        self.assertIsNotNone(tip_data)
        self.assertEqual(tip_data['title'], 'Pomodoro for Coders')

        # 6. Start Your Journey verification
        journey_data = data['start_your_journey']
        self.assertTrue(journey_data['is_authenticated'])
        self.assertEqual(journey_data['enrolled_courses_count'], 1)
        self.assertEqual(journey_data['certificates_earned_count'], 1)
        self.assertIsNotNone(journey_data['primary_resume_course'])
        self.assertEqual(journey_data['primary_resume_course']['progress_percentage'], 45)
        self.assertEqual(journey_data['latest_certificate']['certificate_code'], 'BAO-AND-2026-001')

    def test_aggregated_home_screen_1_guest(self):
        url = reverse('home-engagement')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # Check guest getting started
        self.assertEqual(data['getting_started']['progress_percentage'], 0)
        self.assertFalse(data['getting_started']['is_completed'])

        # Check guest start your journey
        journey = data['start_your_journey']
        self.assertFalse(journey['is_authenticated'])
        self.assertEqual(journey['journey_state'], 'guest')
        self.assertIsNotNone(journey['recommended_starter_course'])
        self.assertEqual(journey['recommended_starter_course']['title'], 'Android App Development with Kotlin')

    def test_individual_getting_started_endpoint(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('home-getting-started')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_steps_count'], 3)

    def test_individual_promotions_endpoint(self):
        url = reverse('home-promotional-banners')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_individual_learning_path_quiz_endpoint(self):
        url = reverse('home-learning-path-quiz')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_available'])

    def test_individual_why_choose_us_endpoint(self):
        url = reverse('home-why-choose-us')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)

    def test_individual_tip_of_the_day_endpoint(self):
        url = reverse('home-tip-of-the-day')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Pomodoro for Coders')

    def test_individual_start_your_journey_endpoint(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('home-start-your-journey')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['enrolled_courses_count'], 1)
