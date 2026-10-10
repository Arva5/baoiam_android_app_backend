from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import (
    Category,
    ContentItem,
    Course,
    CourseBookmark,
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

    def test_content_play_url_requires_enrollment(self):
        play_url = reverse('content-play', kwargs={'id': self.content.id})
        unauth = self.client.get(play_url)
        self.assertEqual(unauth.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user)
        forbidden = self.client.get(play_url)
        self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)

        CourseEnrollment.objects.create(user=self.user, course=self.course)
        ok = self.client.get(play_url)
        self.assertEqual(ok.status_code, status.HTTP_200_OK)
        self.assertEqual(ok.data['url'], 'https://example.com/video.mp4')
        self.assertEqual(ok.data['play_url'], 'https://example.com/video.mp4')
        self.assertEqual(ok.data['mime_type'], 'video/mp4')
        self.assertEqual(ok.data['content_id'], self.content.id)

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

    def test_search_courses_by_title(self):
        url = reverse('course-list')
        response = self.client.get(url, {'search': 'masterclass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [c['title'] for c in response.data]
        self.assertIn('UI/UX Design Masterclass', titles)
        self.assertNotIn('Business Strategy 101', titles)

    def test_search_courses_by_short_code(self):
        url = reverse('course-list')
        response = self.client.get(url, {'search': 'BS101'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [c['title'] for c in response.data]
        self.assertIn('Business Strategy 101', titles)
        self.assertNotIn('UI/UX Design Masterclass', titles)

    def test_search_courses_by_instructor_name(self):
        instructor = User.objects.create_user(email='prof@example.com', name='Professor John', password='Pass123!')
        Course.objects.create(
            title='Advanced Python Frameworks',
            slug='adv-py-frameworks',
            short_code='PY-ADV',
            instructor=instructor,
            instructor_name='Professor John',
            price=Decimal('50.00'),
            is_published=True,
        )
        url = reverse('course-list')
        response = self.client.get(url, {'search': 'Professor John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [c['title'] for c in response.data]
        self.assertIn('Advanced Python Frameworks', titles)

    def test_search_courses_case_insensitive(self):
        url = reverse('course-list')
        res_upper = self.client.get(url, {'search': 'DESIGN'})
        res_lower = self.client.get(url, {'search': 'design'})
        self.assertEqual(res_upper.status_code, status.HTTP_200_OK)
        self.assertEqual(res_lower.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_upper.data), len(res_lower.data))
        titles = [c['title'] for c in res_upper.data]
        self.assertIn('UI/UX Design Masterclass', titles)

    def test_search_courses_combined_with_category_and_filters(self):
        url = reverse('course-list')
        # Search 'strategy' with category 'business'
        response = self.client.get(url, {'search': 'strategy', 'category': 'business'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['slug'], 'business-strategy-101')

        # Search 'strategy' with category 'technology' (should return empty)
        response_wrong_cat = self.client.get(url, {'search': 'strategy', 'category': 'technology'})
        self.assertEqual(response_wrong_cat.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_wrong_cat.data), 0)

    def test_search_courses_no_results(self):
        url = reverse('course-list')
        response = self.client.get(url, {'search': 'nonexistenttermxyz999'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

<<<<<<< HEAD


class CourseSaveApiTests(APITestCase):
    """Save / Unsave / Saved list: har user ke liye alag, duplicate nahi, is_saved sahi."""

    def setUp(self):
        self.user = User.objects.create_user(email='a@example.com', name='A', password='Password123!')
        self.other = User.objects.create_user(email='b@example.com', name='B', password='Password123!')
        self.c1 = Course.objects.create(title='Course One', slug='course-one', is_published=True)
        self.c2 = Course.objects.create(title='Course Two', slug='course-two', is_published=True)
        self.draft = Course.objects.create(title='Draft Course', slug='draft-course', is_published=False)

    def _save_url(self, course):
        return reverse('course-save-id', kwargs={'id': course.id})

    def test_all_three_endpoints_need_auth(self):
        self.assertEqual(self.client.post(self._save_url(self.c1)).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.delete(self._save_url(self.c1)).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.get(reverse('saved-courses-list')).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_save_returns_clear_response(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(self._save_url(self.c1))
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, {
            'success': True,
            'message': 'Course saved successfully.',
            'course_id': self.c1.id,
            'is_saved': True,
        })

    def test_same_user_cannot_save_same_course_twice(self):
        self.client.force_authenticate(user=self.user)
        first = self.client.post(self._save_url(self.c1))
        second = self.client.post(self._save_url(self.c1))
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertTrue(second.data['success'])
        self.assertTrue(second.data['is_saved'])
        self.assertEqual(CourseBookmark.objects.filter(user=self.user, course=self.c1).count(), 1)

    def test_unsave_and_unsave_again(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self._save_url(self.c1))
        res = self.client.delete(self._save_url(self.c1))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'success': True,
            'message': 'Course removed from saved courses.',
            'course_id': self.c1.id,
            'is_saved': False,
        })
        again = self.client.delete(self._save_url(self.c1))
        self.assertEqual(again.status_code, status.HTTP_200_OK)
        self.assertFalse(again.data['is_saved'])
        self.assertEqual(again.data['message'], 'Course was not in your saved courses.')

    def test_unknown_course_gives_404_with_same_shape(self):
        self.client.force_authenticate(user=self.user)
        for method in (self.client.post, self.client.delete):
            res = method(reverse('course-save-id', kwargs={'id': 99999}))
            self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(res.data, {
                'success': False,
                'message': 'Course not found.',
                'course_id': 99999,
                'is_saved': False,
            })

    def test_draft_course_cannot_be_saved_by_normal_user(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(self._save_url(self.draft))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(CourseBookmark.objects.filter(course=self.draft).exists())

    def test_save_by_slug(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(reverse('course-save-slug', kwargs={'slug': 'course-one'}))
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['course_id'], self.c1.id)

    def test_save_is_per_user(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self._save_url(self.c1))

        self.client.force_authenticate(user=self.other)
        detail = self.client.get(reverse('course-detail', kwargs={'id': self.c1.id}))
        self.assertFalse(detail.data['is_saved'])
        self.assertEqual(self.client.get(reverse('saved-courses-list')).data, [])

        self.client.force_authenticate(user=self.user)
        detail = self.client.get(reverse('course-detail', kwargs={'id': self.c1.id}))
        self.assertTrue(detail.data['is_saved'])

    def test_is_saved_in_list_and_detail(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self._save_url(self.c1))

        listing = self.client.get(reverse('course-list'))
        flags = {c['id']: c['is_saved'] for c in listing.data}
        self.assertTrue(flags[self.c1.id])
        self.assertFalse(flags[self.c2.id])

        detail = self.client.get(reverse('course-detail-slug', kwargs={'slug': 'course-one'}))
        self.assertTrue(detail.data['is_saved'])

        self.client.delete(self._save_url(self.c1))
        detail = self.client.get(reverse('course-detail', kwargs={'id': self.c1.id}))
        self.assertFalse(detail.data['is_saved'])

    def test_is_saved_false_for_anonymous(self):
        listing = self.client.get(reverse('course-list'))
        self.assertTrue(all(c['is_saved'] is False for c in listing.data))

    def test_saved_list_same_structure_as_course_list_and_newest_first(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self._save_url(self.c1))
        self.client.post(self._save_url(self.c2))

        saved = self.client.get(reverse('saved-courses-list'))
        self.assertEqual(saved.status_code, status.HTTP_200_OK)
        self.assertEqual([c['id'] for c in saved.data], [self.c2.id, self.c1.id])
        self.assertTrue(all(c['is_saved'] is True for c in saved.data))

        listing = self.client.get(reverse('course-list'))
        from_list = next(c for c in listing.data if c['id'] == self.c1.id)
        from_saved = next(c for c in saved.data if c['id'] == self.c1.id)
        self.assertEqual(set(from_saved.keys()), set(from_list.keys()))

    def test_saved_list_hides_course_that_was_unpublished_later(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(self._save_url(self.c1))
        Course.objects.filter(pk=self.c1.pk).update(is_published=False)
        self.assertEqual(self.client.get(reverse('saved-courses-list')).data, [])
        # par user use hata sakta hai
        res = self.client.delete(self._save_url(self.c1))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_urls_work_without_trailing_slash(self):
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.post(f'/api/courses/{self.c1.id}/save').status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.client.get('/api/courses/saved').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.delete(f'/api/courses/{self.c1.id}/save').status_code, status.HTTP_200_OK)
=======
    def test_limited_time_offers_endpoint(self):
        url = reverse('limited-time-offers')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertLessEqual(len(response.data), 3)

    def test_limited_time_offers_returns_exactly_3_and_serializes_fields(self):
        # Create extra courses with discounts to ensure there are at least 5
        Course.objects.create(
            title='Offer Course 1',
            slug='offer-course-1',
            price=Decimal('100.00'),
            discounted_price=Decimal('50.00'),
            is_published=True,
        )
        Course.objects.create(
            title='Offer Course 2',
            slug='offer-course-2',
            price=Decimal('120.00'),
            discounted_price=Decimal('60.00'),
            is_published=True,
        )
        Course.objects.create(
            title='Offer Course 3',
            slug='offer-course-3',
            price=Decimal('150.00'),
            discounted_price=Decimal('70.00'),
            is_published=True,
        )
        Course.objects.create(
            title='Offer Course 4',
            slug='offer-course-4',
            price=Decimal('200.00'),
            discounted_price=Decimal('80.00'),
            is_published=True,
        )
        # Create an unpublished course which should not be in the results
        Course.objects.create(
            title='Unpublished Offer Course',
            slug='unpublished-offer-course',
            price=Decimal('300.00'),
            discounted_price=Decimal('90.00'),
            is_published=False,
        )

        response = self.client.get('/api/courses/limited-time-offers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        # Verify serialized fields
        first_course = response.data[0]
        self.assertIn('id', first_course)
        self.assertIn('title', first_course)
        self.assertIn('slug', first_course)
        self.assertIn('price', first_course)
        self.assertIn('discounted_price', first_course)
        self.assertIn('is_enrolled', first_course)
        # Ensure unpublished course is not included
        slugs = [c['slug'] for c in response.data]
        self.assertNotIn('unpublished-offer-course', slugs)

>>>>>>> 3c303fb8c56ed3294d6afa4d535b57836172ec06
