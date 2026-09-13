from django.db import models


class AboutOverview(models.Model):
    """
    Company Overview / Mission information and trusted partner brands.
    Single configuration record for the About Us screen.
    """
    DEFAULT_MISSION = (
        "To democratize education by providing accessible, high-quality learning "
        "experiences that empower learners worldwide to achieve their full potential."
    )
    DEFAULT_TRUSTED_BY = ["TechCorp", "EduPlus", "SkillHub", "LearnCo"]

    title = models.CharField(max_length=200, default="About Us")
    subtitle = models.CharField(max_length=255, blank=True, default="Empowering learners worldwide")
    mission_text = models.TextField(default=DEFAULT_MISSION)
    vision_text = models.TextField(blank=True, default="")
    trusted_by_labels = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Us Overview"
        verbose_name_plural = "About Us Overview"

    def __str__(self):
        return self.title

    @classmethod
    def get_solo(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create(
                mission_text=cls.DEFAULT_MISSION,
                trusted_by_labels=cls.DEFAULT_TRUSTED_BY,
            )
        return obj


class ImpactStat(models.Model):
    """
    Key platform impact statistics shown on the About Us screen.
    e.g. ("1M+", "Students", "Groups")
    """
    value = models.CharField(max_length=50, help_text="e.g. 1M+, 5000+, 98%, 150+")
    label = models.CharField(max_length=100, help_text="e.g. Students, Courses, Success Rate, Countries")
    icon = models.CharField(
        max_length=100,
        default="Groups",
        help_text="Material Icon name e.g. Groups, MenuBook, Star, Public",
    )
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = "Impact Stat"
        verbose_name_plural = "Impact Stats"

    def __str__(self):
        return f"{self.value} {self.label}"


class WhyChooseUsItem(models.Model):
    """
    What We Offer / Why Choose Us features shown on the About Us screen.
    e.g. ("Expert Instructors", "Learn from industry professionals", "School")
    """
    title = models.CharField(max_length=150)
    description = models.TextField()
    icon = models.CharField(
        max_length=100,
        default="School",
        help_text="Material Icon name e.g. School, VideoCall, SupportAgent, PhoneAndroid, WorkspacePremium, TrendingUp",
    )
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = "Why Choose Us / Offer Item"
        verbose_name_plural = "Why Choose Us / Offer Items"

    def __str__(self):
        return self.title


class SuccessStory(models.Model):
    """
    Student or learner testimonials / success stories.
    e.g. ("Peter Jones", "UNIV Business School", 5, "The interactive learning...")
    """
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150, help_text="e.g. UNIV Business School, Web Developer")
    rating = models.PositiveSmallIntegerField(default=5)
    story = models.TextField()
    image_url = models.URLField(blank=True, default="")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, help_text="Approval status (visible if true)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = "Success Story"
        verbose_name_plural = "Success Stories"

    def __str__(self):
        return f"{self.name} ({self.role}) - {self.rating}★"


class TeamMember(models.Model):
    """
    Core leadership and team members.
    e.g. ("James Perkins", "CEO & Founder")
    """
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150, help_text="e.g. CEO & Founder, Head of Education")
    bio = models.TextField(blank=True, default="")
    image_url = models.URLField(blank=True, default="")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.name} - {self.role}"
