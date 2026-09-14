from django.core.management.base import BaseCommand
from about.models import AboutOverview, ImpactStat, WhyChooseUsItem, SuccessStory, TeamMember


class Command(BaseCommand):
    help = "Seed initial About Us data matching Kotlin AboutUsUiState"

    def handle(self, *args, **options):
        self.stdout.write("Seeding About Us module data...")

        # 1. Overview
        overview, created = AboutOverview.objects.get_or_create(
            id=1,
            defaults={
                "title": "About Us",
                "subtitle": "Empowering learners worldwide",
                "mission_text": (
                    "To democratize education by providing accessible, high-quality learning "
                    "experiences that empower learners worldwide to achieve their full potential."
                ),
                "vision_text": "To be the leading global learning platform for personal and professional career growth.",
                "trusted_by_labels": ["TechCorp", "EduPlus", "SkillHub", "LearnCo"],
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("[OK] Created AboutOverview"))
        else:
            self.stdout.write("- AboutOverview already exists")

        # 2. Impact Stats
        stats = [
            {"value": "1M+", "label": "Students", "icon": "Groups", "display_order": 1},
            {"value": "5000+", "label": "Courses", "icon": "MenuBook", "display_order": 2},
            {"value": "98%", "label": "Success Rate", "icon": "Star", "display_order": 3},
            {"value": "150+", "label": "Countries", "icon": "Public", "display_order": 4},
        ]
        for s in stats:
            obj, created = ImpactStat.objects.get_or_create(
                label=s["label"],
                defaults={
                    "value": s["value"],
                    "icon": s["icon"],
                    "display_order": s["display_order"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"[OK] Created Stat: {obj.value} {obj.label}"))

        # 3. Why Choose Us / What We Offer
        offers = [
            {"title": "Expert Instructors", "description": "Learn from industry professionals", "icon": "School", "display_order": 1},
            {"title": "Live Classes", "description": "Interactive learning experience", "icon": "VideoCall", "display_order": 2},
            {"title": "24/7 Support", "description": "Always here to help you", "icon": "SupportAgent", "display_order": 3},
            {"title": "Mobile Learning", "description": "Learn on the go, anywhere", "icon": "PhoneAndroid", "display_order": 4},
            {"title": "Certification", "description": "Industry-recognized credentials", "icon": "WorkspacePremium", "display_order": 5},
            {"title": "Personal Growth", "description": "Achieve your career goals", "icon": "TrendingUp", "display_order": 6},
        ]
        for o in offers:
            obj, created = WhyChooseUsItem.objects.get_or_create(
                title=o["title"],
                defaults={
                    "description": o["description"],
                    "icon": o["icon"],
                    "display_order": o["display_order"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"[OK] Created Offer: {obj.title}"))

        # 4. Success Stories (Indian dummy names)
        # Clean up old English placeholder records if present
        SuccessStory.objects.filter(name__in=["Peter Jones", "Mia Morris"]).delete()

        stories = [
            {
                "name": "Aarav Sharma",
                "role": "UNIV Business School",
                "rating": 5,
                "story": "The interactive learning app took my skills to the next level. I landed my dream job right after completing the program.",
                "display_order": 1,
            },
            {
                "name": "Priya Patel",
                "role": "Web Developer",
                "rating": 5,
                "story": "The practical projects and mentor support were invaluable in helping me transition into web development.",
                "display_order": 2,
            },
        ]
        for st in stories:
            obj, _ = SuccessStory.objects.update_or_create(
                display_order=st["display_order"],
                defaults={
                    "name": st["name"],
                    "role": st["role"],
                    "rating": st["rating"],
                    "story": st["story"],
                    "is_active": True,
                },
            )
            self.stdout.write(self.style.SUCCESS(f"[OK] Story: {obj.name} ({obj.role})"))

        # 5. Team Members (Indian dummy names)
        # Clean up old English placeholder records if present
        TeamMember.objects.filter(name__in=["James Perkins", "Emma Wilson"]).delete()

        team = [
            {"name": "Vikram Sharma", "role": "CEO & Founder", "display_order": 1},
            {"name": "Dr. Neha Verma", "role": "Head of Education", "display_order": 2},
        ]
        for t in team:
            obj, _ = TeamMember.objects.update_or_create(
                display_order=t["display_order"],
                defaults={
                    "name": t["name"],
                    "role": t["role"],
                    "is_active": True,
                },
            )
            self.stdout.write(self.style.SUCCESS(f"[OK] Team Member: {obj.name} ({obj.role})"))

        self.stdout.write(self.style.SUCCESS("All About Us initial data seeded successfully!"))
