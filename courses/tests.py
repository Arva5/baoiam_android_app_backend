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
        self.category, _ = Category.objects.get_or_create(
            slug='design',
            defaults={'name': 'Design', 'order': 2, 'is_active': True}
        )
        self.business_category, _ = Category.objects.get_or_create(
            slug='business',
            defaults={'name': 'Business', 'order': 1, 'is_active': True}
        )
        self.tech_category, _ = Category.objects.get_or_create(
            slug='technology',
            defaults={'name': 'Technology', 'order': 3, 'is_active': True}
        )
        self.dev_category, _ = Category.objects.get_or_create(
            slug='development',
            defaults={'name': 'Development', 'order': 4, 'is_active': True}
        )

        self.course = Course.objects.create(
            title='UI/UX Design Masterclass',
            slug='ui-ux-design',
            short_code='UI/UX',
            category=self.category,
            price=Decimal('29.99'),
            level='beginner',
            is_published=True,
        )
        self.business_course = Course.objects.create(
            title='Business Strategy 101',
            slug='business-strategy-101',
            short_code='BS101',
            category=self.business_category,
            price=Decimal('49.99'),
            level='intermediate',
            is_published=True,
        )
        self.tech_course = Course.objects.create(
            title='Applied AI & Machine Learning',
            slug='applied-ai-ml',
            short_code='AI-ML',
            category=self.tech_category,
            price=Decimal('79.99'),
            level='advanced',
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
        self.assertGreaterEqual(len(response.data), 3)

    def test_filter_courses_by_category_slug(self):
        url = reverse('course-list')

        # Filter by design
        res_design = self.client.get(url, {'category': 'design'})
        self.assertEqual(res_design.status_code, status.HTTP_200_OK)
        titles = [c['title'] for c in res_design.data]
        self.assertIn('UI/UX Design Masterclass', titles)
        self.assertNotIn('Business Strategy 101', titles)
        self.assertNotIn('Applied AI & Machine Learning', titles)

        # Filter by business (case-insensitive)
        res_business = self.client.get(url, {'category': 'Business'})
        self.assertEqual(res_business.status_code, status.HTTP_200_OK)
        titles_biz = [c['title'] for c in res_business.data]
        self.assertIn('Business Strategy 101', titles_biz)
        self.assertNotIn('UI/UX Design Masterclass', titles_biz)

        # Filter by technology
        res_tech = self.client.get(url, {'category': 'technology'})
        self.assertEqual(res_tech.status_code, status.HTTP_200_OK)
        titles_tech = [c['title'] for c in res_tech.data]
        self.assertIn('Applied AI & Machine Learning', titles_tech)

        # Filter by category with zero courses
        res_dev = self.client.get(url, {'category': 'development'})
        self.assertEqual(res_dev.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_dev.data), 0)

        # Filter by non-existent category
        res_none = self.client.get(url, {'category': 'non-existent-category'})
        self.assertEqual(res_none.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_none.data), 0)

    def test_filter_courses_by_category_and_level(self):
        url = reverse('course-list')
        res = self.client.get(url, {'category': 'design', 'level': 'beginner'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['slug'], 'ui-ux-design')

    def test_course_detail_by_id(self):
        url = reverse('course-detail', kwargs={'id': self.course.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'UI/UX Design Masterclass')
        self.assertEqual(response.data['category'], self.category.id)
        self.assertEqual(response.data['category_name'], 'Design')
        self.assertIn('modules', response.data)
        self.assertEqual(len(response.data['modules']), 1)

    def test_course_detail_by_slug(self):
        url = reverse('course-detail-slug', kwargs={'slug': 'ui-ux-design'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'UI/UX Design Masterclass')
        self.assertEqual(response.data['category'], self.category.id)
        self.assertEqual(response.data['category_name'], 'Design')

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
        self.assertGreaterEqual(len(response.data), 4)

        slugs = [cat['slug'] for cat in response.data]
        self.assertIn('business', slugs)
        self.assertIn('design', slugs)
        self.assertIn('technology', slugs)
        self.assertIn('development', slugs)

        # Verify fields in category response
        first_cat = response.data[0]
        self.assertIn('id', first_cat)
        self.assertIn('name', first_cat)
        self.assertIn('slug', first_cat)
        self.assertIn('description', first_cat)
        self.assertIn('order', first_cat)
        self.assertIn('is_active', first_cat)

    def test_inactive_category_excluded_from_list(self):
        Category.objects.create(name='Archived Cat', slug='archived-cat', is_active=False)
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = [cat['slug'] for cat in response.data]
        self.assertNotIn('archived-cat', slugs)

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
