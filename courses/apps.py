from django.apps import AppConfig
from django.db.models.signals import post_migrate


def auto_seed_courses(sender, **kwargs):
    if sender.name == 'courses':
        try:
            from django.core.management import call_command
            from .models import Course
            import os
            from django.conf import settings

            # If course 9 is missing or total courses < 9, seed automatically
            if not Course.objects.filter(id=9).exists() or Course.objects.count() < 9:
                print("[AUTO-SEED] Seeding dummy courses for Render...")
                call_command('seed_dummy_courses')
                print("[AUTO-SEED] Seeded dummy courses successfully.")
        except Exception as e:
            print(f"[AUTO-SEED] Warning: Could not auto-seed courses: {e}")


class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'

    def ready(self):
        post_migrate.connect(auto_seed_courses, sender=self)
