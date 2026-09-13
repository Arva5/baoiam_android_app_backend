from django.core.management.base import BaseCommand

from courses.models import Category, Course


CATEGORY_DATA = {
    'business': {
        'name': 'Business',
        'description': 'Courses covering entrepreneurship, management, marketing, sales, and business strategy.',
        'order': 1,
        'is_active': True,
    },
    'design': {
        'name': 'Design',
        'description': 'Courses covering UI/UX design, graphic design, design systems, and digital product design.',
        'order': 2,
        'is_active': True,
    },
    'technology': {
        'name': 'Technology',
        'description': 'Courses covering artificial intelligence, cloud computing, cybersecurity, and data science.',
        'order': 3,
        'is_active': True,
    },
    'development': {
        'name': 'Development',
        'description': 'Courses covering full-stack web development, mobile apps, DevOps, and backend engineering.',
        'order': 4,
        'is_active': True,
    },
}

COURSE_DATA = [
    {
        'slug': 'uiux-design-fundamentals',
        'title': 'UI/UX Design Fundamentals',
        'short_code': 'UI/UX',
        'category_slug': 'design',
        'is_published': True,
    },
    {
        'slug': 'unpublished-draft-course',
        'title': 'Unpublished Draft Course',
        'short_code': 'DR',
        'category_slug': None,
        'is_published': False,
    },
    {
        'slug': 'python-mastery',
        'title': 'Complete Python Bootcamp',
        'short_code': 'PY-101',
        'category_slug': 'development',
        'is_published': True,
    },
    {
        'slug': 'business-analytics-python',
        'title': 'Business Analytics with Python',
        'short_code': 'BA-PY',
        'category_slug': 'business',
        'is_published': True,
    },
]


class Command(BaseCommand):
    help = 'Seed the four local courses and their categories (idempotent).'

    def handle(self, *args, **options):
        categories = {}
        for slug, data in CATEGORY_DATA.items():
            category, created = Category.objects.update_or_create(
                slug=slug,
                defaults=data,
            )
            categories[slug] = category
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'{action} category: {category.name}')

        for course_data in COURSE_DATA:
            data = course_data.copy()
            category_slug = data.pop('category_slug')
            data['category'] = categories.get(category_slug)
            course, created = Course.objects.update_or_create(
                slug=data.pop('slug'),
                defaults=data,
            )
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'{action} course: {course.title}')

        self.stdout.write(self.style.SUCCESS('Courses seeded successfully.'))