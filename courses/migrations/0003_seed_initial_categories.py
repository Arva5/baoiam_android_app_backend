# Data migration to seed initial course categories: Business, Design, Technology, Development

from django.db import migrations

INITIAL_CATEGORIES = [
    {
        'name': 'Business',
        'slug': 'business',
        'description': 'Courses covering entrepreneurship, management, marketing, sales, and business strategy.',
        'order': 1,
        'is_active': True,
    },
    {
        'name': 'Design',
        'slug': 'design',
        'description': 'Courses covering UI/UX design, graphic design, design systems, and digital product design.',
        'order': 2,
        'is_active': True,
    },
    {
        'name': 'Technology',
        'slug': 'technology',
        'description': 'Courses covering artificial intelligence, cloud computing, cybersecurity, and data science.',
        'order': 3,
        'is_active': True,
    },
    {
        'name': 'Development',
        'slug': 'development',
        'description': 'Courses covering full-stack web development, mobile apps, DevOps, and backend engineering.',
        'order': 4,
        'is_active': True,
    },
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('courses', 'Category')
    for cat_data in INITIAL_CATEGORIES:
        Category.objects.update_or_create(
            slug=cat_data['slug'],
            defaults={
                'name': cat_data['name'],
                'description': cat_data['description'],
                'order': cat_data['order'],
                'is_active': cat_data['is_active'],
            }
        )


def remove_categories(apps, schema_editor):
    Category = apps.get_model('courses', 'Category')
    slugs = [c['slug'] for c in INITIAL_CATEGORIES]
    Category.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_sync_courses_schema'),
    ]

    operations = [
        migrations.RunPython(seed_categories, reverse_code=remove_categories),
    ]
