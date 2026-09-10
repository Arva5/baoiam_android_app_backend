"""
Management command: seed_discovery_quiz
Creates (or updates) the Course Discovery Quiz with exactly 5 questions.
Safe to run multiple times — fully idempotent.

Usage:
    python manage.py seed_discovery_quiz
    python manage.py seed_discovery_quiz --reset   # deletes & recreates
"""
from django.core.management.base import BaseCommand

from assessments.models import Assessment, Option, Question

QUIZ_DATA = {
    "title": "Course Discovery Quiz",
    "subtitle": "Find your perfect learning path in under 2 minutes",
    "description": (
        "Answer 5 quick questions and we will recommend the best courses "
        "tailored to your interests, schedule, and experience level."
    ),
    "quiz_type": "career_path",
    "estimated_minutes": 2,
    "badge_text": "POPULAR QUIZ",
    "is_featured": True,
    "is_active": True,
}

# Each question: (order, question_text, [(option_text, career_track, order), ...])
QUESTIONS = [
    (
        1,
        "What type of programming are you most interested in?",
        [
            ("Web Development",    "web",    1),
            ("Mobile Development", "mobile", 2),
            ("Data Science",       "data",   3),
            ("Game Development",   "game",   4),
        ],
    ),
    (
        2,
        "How much time can you dedicate to learning each week?",
        [
            ("Less than 2 hours", "low",    1),
            ("2-5 hours",         "medium", 2),
            ("5-10 hours",        "high",   3),
            ("10+ hours",         "very_high", 4),
        ],
    ),
    (
        3,
        "What's your current experience level?",
        [
            ("Complete Beginner", "beginner",     1),
            ("Some Experience",   "beginner",     2),
            ("Intermediate",      "intermediate", 3),
            ("Advanced",          "advanced",     4),
        ],
    ),
    (
        4,
        "What's your main learning goal?",
        [
            ("Career Change",          "career_change", 1),
            ("Skill Upgrade",          "skill_upgrade",  2),
            ("Personal Hobby",         "hobby",          3),
            ("Academic Requirement",   "academic",       4),
        ],
    ),
    (
        5,
        "How do you prefer to learn?",
        [
            ("Video Lectures",    "video",    1),
            ("Reading Material",  "reading",  2),
            ("Hands-on Practice", "practice", 3),
            ("Mixed Approach",    "mixed",    4),
        ],
    ),
]

class Command(BaseCommand):
    help = "Seed the Course Discovery Quiz (idempotent)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete the existing quiz and recreate it from scratch.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = Assessment.objects.filter(title=QUIZ_DATA["title"]).delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing quiz record(s)."))

        assessment, created = Assessment.objects.get_or_create(
            title=QUIZ_DATA["title"],
            defaults=QUIZ_DATA,
        )
        if not created:
            # Update metadata fields in case they changed
            for field, value in QUIZ_DATA.items():
                setattr(assessment, field, value)
            assessment.save()
            self.stdout.write(f"Quiz already existed — metadata refreshed.")
        else:
            self.stdout.write(self.style.SUCCESS(f"Created quiz: {assessment.title}"))

        Assessment.objects.exclude(pk=assessment.pk).filter(is_featured=True).update(is_featured=False)

        seeded_orders = []
        for q_order, q_text, options_data in QUESTIONS:
            question, q_created = Question.objects.get_or_create(
                assessment=assessment,
                order=q_order,
                defaults={"question_text": q_text, "is_active": True},
            )
            if not q_created:
                question.question_text = q_text
                question.is_active = True
                question.save()

            seeded_orders.append(q_order)
            option_orders = []
            for opt_text, career_track, opt_order in options_data:
                option_orders.append(opt_order)
                opt, opt_created = Option.objects.get_or_create(
                    question=question,
                    order=opt_order,
                    defaults={"option_text": opt_text, "career_track": career_track},
                )
                if not opt_created:
                    opt.option_text = opt_text
                    opt.career_track = career_track
                    opt.save()
            question.options.exclude(order__in=option_orders).delete()

            action = "Created" if q_created else "Updated"
            self.stdout.write(f"  {action} Q{q_order}: {q_text[:60]}")

        Question.objects.filter(assessment=assessment).exclude(order__in=seeded_orders).update(is_active=False)

        self.stdout.write(self.style.SUCCESS("Course Discovery Quiz seeded successfully."))
