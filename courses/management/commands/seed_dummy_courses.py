"""
Dummy courses + videos seed karta hai (ContentItem.url me playable MP4).

Use:
  python manage.py seed_dummy_courses
  python manage.py seed_dummy_courses --r2-base-url https://pub-xxxx.r2.dev
  python manage.py seed_dummy_courses --only-if-empty
  python manage.py seed_dummy_courses --reset
  python manage.py seed_dummy_courses --enroll-email student@test.com
"""
import os
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from courses.models import Category, ContentItem, Course, CourseEnrollment, CourseModule, Lesson

G = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample"
PDF = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

DUMMY = [
    {
        "title": "Python for Beginners",
        "short_code": "PY",
        "subtitle": "Zero se Python: variables, loops, functions",
        "description": "Python zero se seekho: variables, loops, functions aur pehla mini project.",
        "thumbnail": "https://picsum.photos/seed/python/640/360",
        "category_slug": "development",
        "level": "beginner",
        "duration_hours": Decimal("8.5"),
        "is_featured": True,
        "is_popular": True,
        "modules": [
            ("Introduction", [
                ("Welcome to the course", [("VIDEO", "Welcome Video", "videos/python/welcome.mp4", f"{G}/BigBuckBunny.mp4", 596)]),
                ("Installing Python", [("VIDEO", "Install Guide", "videos/python/install.mp4", f"{G}/ElephantsDream.mp4", 653)]),
            ]),
            ("Python Basics", [
                ("Variables and Data Types", [
                    ("VIDEO", "Variables Lecture", "videos/python/variables.mp4", f"{G}/Sintel.mp4", 888),
                    ("PDF", "Cheat Sheet", "pdfs/python/cheatsheet.pdf", PDF, 0)]),
            ]),
        ],
    },
    {
        "title": "Android Development with Kotlin",
        "short_code": "AND",
        "subtitle": "Kotlin aur Jetpack Compose se pehli app",
        "description": "Kotlin aur Jetpack Compose se apni pehli Android app banao.",
        "thumbnail": "https://picsum.photos/seed/android/640/360",
        "category_slug": "development",
        "level": "intermediate",
        "duration_hours": Decimal("12.0"),
        "is_featured": True,
        "is_popular": False,
        "modules": [
            ("Getting Started", [
                ("Setting up Android Studio", [("VIDEO", "Setup Video", "videos/android/setup.mp4", f"{G}/TearsOfSteel.mp4", 734)]),
            ]),
            ("Jetpack Compose", [
                ("First Composable", [("VIDEO", "Composable Basics", "videos/android/compose.mp4", f"{G}/ForBiggerBlazes.mp4", 15)]),
            ]),
        ],
    },
    {
        "title": "UI/UX Design Basics",
        "short_code": "UX",
        "subtitle": "Figma ke saath design ki basics",
        "description": "Figma ke saath design ki basics: UX thinking, color, aur wireframes.",
        "thumbnail": "https://picsum.photos/seed/uiux/640/360",
        "category_slug": "design",
        "level": "beginner",
        "duration_hours": Decimal("6.0"),
        "is_featured": False,
        "is_popular": True,
        "modules": [
            ("Design Fundamentals", [
                ("What is UX?", [("VIDEO", "UX Intro", "videos/uiux/intro.mp4", f"{G}/ForBiggerEscapes.mp4", 15)]),
                ("Color Theory", [("VIDEO", "Colors", "videos/uiux/colors.mp4", f"{G}/ForBiggerJoyrides.mp4", 15)]),
            ]),
        ],
    },
]


class Command(BaseCommand):
    help = "Dummy courses, modules, lessons aur video ContentItems banata hai."

    def add_arguments(self, parser):
        parser.add_argument("--r2-base-url", default=os.environ.get("R2_PUBLIC_BASE_URL", ""), help="R2 public URL, e.g. https://pub-xxxx.r2.dev")
        parser.add_argument("--enroll-email", default="", help="Is user ko dummy courses me enroll karo (testing ke liye)")
        parser.add_argument("--only-if-empty", action="store_true", help="Agar koi course pehle se hai to kuch mat karo")
        parser.add_argument("--reset", action="store_true", help="Pehle dummy courses delete karo")

    def handle(self, *args, **opts):
        if opts["only_if_empty"] and Course.objects.exists():
            self.stdout.write("Courses already exist, seed skipped.")
            return
        base = opts["r2_base_url"].rstrip("/")
        instructor = get_user_model().objects.filter(is_staff=True).first()

        if opts["reset"]:
            titles = [c["title"] for c in DUMMY]
            n, _ = Course.objects.filter(title__in=titles).delete()
            self.stdout.write(f"Deleted {n} old rows")

        for c in DUMMY:
            category = Category.objects.filter(slug=c["category_slug"]).first()
            course, created = Course.objects.get_or_create(
                title=c["title"],
                defaults=dict(
                    slug=slugify(c["title"]),
                    short_code=c["short_code"],
                    subtitle=c["subtitle"],
                    description=c["description"],
                    thumbnail_url=c["thumbnail"],
                    cover_image_url=c["thumbnail"],
                    category=category,
                    level=c["level"],
                    duration_hours=c["duration_hours"],
                    price=Decimal("0.00"),
                    is_featured=c["is_featured"],
                    is_popular=c["is_popular"],
                    is_published=True,
                    instructor=instructor,
                    instructor_name=instructor.name if instructor else "Baoiam Instructor",
                ),
            )
            if not created:
                CourseModule.objects.filter(course=course).delete()
                course.subtitle = c["subtitle"]
                course.description = c["description"]
                course.category = category
                course.level = c["level"]
                course.price = Decimal("0.00")
                course.is_published = True
                course.save()
            lesson_total = 0
            for m_order, (m_title, lessons) in enumerate(c["modules"], start=1):
                module = CourseModule.objects.create(course=course, title=m_title, order=m_order)
                for l_order, (l_title, items) in enumerate(lessons, start=1):
                    lesson = Lesson.objects.create(module=module, title=l_title, order=l_order, published_at=date.today())
                    lesson_total += 1
                    for i_order, (ctype, i_title, key, sample, dur) in enumerate(items, start=1):
                        url = f"{base}/{key}" if base else sample
                        ContentItem.objects.create(
                            lesson=lesson,
                            content_type=ctype,
                            title=i_title,
                            url=url,
                            storage_key=key,
                            duration_seconds=dur or None,
                            order=i_order,
                        )
            course.lessons_count = lesson_total
            course.save(update_fields=["lessons_count"])
            if opts["enroll_email"]:
                user = get_user_model().objects.filter(email__iexact=opts["enroll_email"]).first()
                if user:
                    CourseEnrollment.objects.get_or_create(
                        user=user,
                        course=course,
                        defaults={"total_lessons": course.total_lectures},
                    )
                else:
                    self.stdout.write(self.style.WARNING(f"User {opts['enroll_email']} nahi mila, enroll skip"))
            self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Refreshed'}: {course.title} ({course.slug})"))
        self.stdout.write(self.style.SUCCESS("Done. Android: GET /api/courses/ then enroll, then GET /api/courses/content/<id>/play/"))
