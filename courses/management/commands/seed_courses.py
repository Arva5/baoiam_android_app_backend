from django.core.management.base import BaseCommand
from courses.models import Category, Course

class Command(BaseCommand):
    help = 'Seeds dummy categories and courses for the Course API.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to seed courses...'))

        # Create categories
        categories_data = [
            'Success Fusion Program',
            'Udaan 90',
            'Technology',
            'Business & Management'
        ]

        categories = {}
        for cat_name in categories_data:
            cat, created = Category.objects.get_or_create(name=cat_name)
            categories[cat_name] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {cat_name}'))
            else:
                self.stdout.write(f'Category already exists: {cat_name}')

        # Create courses
        courses_data = [
            {
                'title': 'Advanced Python Web Development',
                'short_code': 'PWD',
                'subtitle': 'Master Django and REST Framework',
                'description': 'A comprehensive guide to building scalable web applications using Python and Django.',
                'thumbnail_url': 'https://placehold.co/400x300/e9ecef/495057?text=Python+Web',
                'cover_image_url': 'https://placehold.co/800x400/e9ecef/495057?text=Python+Web+Cover',
                'instructor_name': 'John Doe',
                'category': categories['Technology'],
                'level': 'advanced',
                'rating': 4.8,
                'reviews_count': 125,
                'duration_hours': 45.5,
                'lessons_count': 120,
                'price': 99.99,
                'discounted_price': 49.99,
                'is_featured': True,
                'is_popular': True,
                'is_published': True,
            },
            {
                'title': 'Business Analytics Fundamentals',
                'short_code': 'BAF',
                'subtitle': 'Data-driven decision making',
                'description': 'Learn how to analyze business data and make informed decisions using modern tools.',
                'thumbnail_url': 'https://placehold.co/400x300/e9ecef/495057?text=Business+Analytics',
                'cover_image_url': 'https://placehold.co/800x400/e9ecef/495057?text=Business+Analytics+Cover',
                'instructor_name': 'Jane Smith',
                'category': categories['Business & Management'],
                'level': 'beginner',
                'rating': 4.6,
                'reviews_count': 89,
                'duration_hours': 20.0,
                'lessons_count': 45,
                'price': 79.99,
                'discounted_price': None,
                'is_featured': False,
                'is_popular': True,
                'is_published': True,
            },
            {
                'title': 'Success Fusion: Leadership',
                'short_code': 'SFL',
                'subtitle': 'Unlock your leadership potential',
                'description': 'Develop the skills needed to lead teams effectively and drive success in any organization.',
                'thumbnail_url': 'https://placehold.co/400x300/e9ecef/495057?text=Leadership',
                'cover_image_url': 'https://placehold.co/800x400/e9ecef/495057?text=Leadership+Cover',
                'instructor_name': 'Dr. Robert Brown',
                'category': categories['Success Fusion Program'],
                'level': 'intermediate',
                'rating': 4.9,
                'reviews_count': 210,
                'duration_hours': 15.0,
                'lessons_count': 30,
                'price': 149.99,
                'discounted_price': 99.99,
                'is_featured': True,
                'is_popular': False,
                'is_published': True,
            },
            {
                'title': 'Udaan 90: Fast Track Career',
                'short_code': 'U90',
                'subtitle': 'Accelerate your career growth in 90 days',
                'description': 'A complete roadmap to boosting your career trajectory within just 90 days.',
                'thumbnail_url': 'https://placehold.co/400x300/e9ecef/495057?text=Udaan+90',
                'cover_image_url': 'https://placehold.co/800x400/e9ecef/495057?text=Udaan+90+Cover',
                'instructor_name': 'Amit Patel',
                'category': categories['Udaan 90'],
                'level': 'all_levels',
                'rating': 4.7,
                'reviews_count': 156,
                'duration_hours': 30.0,
                'lessons_count': 90,
                'price': 199.99,
                'discounted_price': 149.99,
                'is_featured': True,
                'is_popular': True,
                'is_published': True,
            },
            {
                'title': 'Full Stack JavaScript',
                'short_code': 'FSJ',
                'subtitle': 'MERN stack development',
                'description': 'Master MongoDB, Express, React, and Node.js to build modern web applications.',
                'thumbnail_url': 'https://placehold.co/400x300/e9ecef/495057?text=Full+Stack',
                'cover_image_url': 'https://placehold.co/800x400/e9ecef/495057?text=Full+Stack+Cover',
                'instructor_name': 'Sarah Johnson',
                'category': categories['Technology'],
                'level': 'intermediate',
                'rating': 4.5,
                'reviews_count': 342,
                'duration_hours': 60.0,
                'lessons_count': 150,
                'price': 129.99,
                'discounted_price': 89.99,
                'is_featured': False,
                'is_popular': True,
                'is_published': True,
            },
        ]

        created_count = 0
        updated_count = 0

        for course_data in courses_data:
            title = course_data.pop('title')
            course, created = Course.objects.update_or_create(
                title=title,
                defaults=course_data
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded courses! Created: {created_count}, Updated: {updated_count}'
        ))