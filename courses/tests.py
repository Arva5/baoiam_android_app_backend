from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import (
    Category,
    ContentItem,
    Course,
    CourseEnrollment,
    CourseModule,
    Lesson,
    PromotionalBanner,
    TipOfTheDay,
    WhyChooseUsItem,
)

User = get_user_model()


class CoursesAppTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='student@example.com',
            name='Student',
            password='Password123!',
        )
        self.category = Category.objects.create(name='Design', slug='design')
        self.course = Course.objects.create(
            title='UI/UX Design Masterclass',
            slug='ui-ux-design',
            short_code='UI/UX',
            category=self.category,
            price=Decimal('29.99'),
            is_published=True,
        )

        self.module = CourseModule.objects.create(
            course=self.course,
            title='Module 1: Foundations',
            order=1,
        )
        self.lesson = Lesson.objects.create(
            module=self.module,
            title='Lecture 1: Introduction',
            order=1,
        )
        self.content = ContentItem.objects.create(
            lesson=self.lesson,
            content_type=ContentItem.ContentType.VIDEO,
            title='Intro Video',
            url='https://example.com/video.mp4',
            duration_seconds=300,
            order=1,
        )

    def test_list_courses(self):
        url = reverse('course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_course_detail_by_id(self):
        url = reverse('course-detail', kwargs={'id': self.course.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'UI/UX Design Masterclass')
        self.assertIn('modules', response.data)
        self.assertEqual(len(response.data['modules']), 1)

    def test_course_detail_by_slug(self):
        url = reverse('course-detail-slug', kwargs={'slug': 'ui-ux-design'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'UI/UX Design Masterclass')

    def test_course_player_unlocked_with_enrollment(self):
        self.client.force_authenticate(user=self.user)
        CourseEnrollment.objects.create(
            user=self.user,
            course=self.course,
            progress_percentage=10,
        )
        url = reverse('course-detail-slug', kwargs={'slug': 'ui-ux-design'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_active_access'])
        self.assertTrue(response.data['is_enrolled'])
        lesson_data = response.data['modules'][0]['lessons'][0]
        self.assertFalse(lesson_data['locked'])
        self.assertEqual(len(lesson_data['content_items']), 1)

    def test_list_categories(self):
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_promotions_and_tips(self):
        PromotionalBanner.objects.create(title='50% Off Flash Sale', is_active=True)
        TipOfTheDay.objects.create(title='Stay Consistent', content='Practice every day.', is_active=True)
        WhyChooseUsItem.objects.create(title='Expert Instructors', description='Learn from leads.', is_active=True)

        res_promo = self.client.get(reverse('promotions-list'))
        self.assertEqual(res_promo.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_promo.data), 1)

        res_tip = self.client.get(reverse('tip-of-the-day'))
        self.assertEqual(res_tip.status_code, status.HTTP_200_OK)
        self.assertEqual(res_tip.data['title'], 'Stay Consistent')

        res_why = self.client.get(reverse('why-choose-us-list'))
        self.assertEqual(res_why.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_why.data), 1)
