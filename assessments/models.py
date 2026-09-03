from django.conf import settings
from django.db import models
from django.utils import timezone


class Assessment(models.Model):
    QUIZ_TYPE_CHOICES = (
        ('career_path', 'Career Path Finder'),
        ('skill_assessment', 'Skill Assessment'),
        ('general', 'General Assessment'),
    )

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    quiz_type = models.CharField(
        max_length=50,
        choices=QUIZ_TYPE_CHOICES,
        default='career_path'
    )
    estimated_minutes = models.PositiveIntegerField(default=3)
    badge_text = models.CharField(max_length=50, blank=True, default='POPULAR QUIZ')
    is_featured = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    @property
    def questions_count(self):
        return self.questions.filter(is_active=True).count()


class Question(models.Model):
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.assessment.title} - Q: {self.question_text[:50]}"


class Option(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options'
    )
    option_text = models.CharField(max_length=255)
    career_track = models.CharField(
        max_length=100,
        blank=True,
        help_text="Target track/recommendation tag (e.g. 'Full Stack Developer', 'Data Scientist')"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.option_text


class UserAssessmentAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assessment_attempts'
    )
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    selected_answers = models.JSONField(default=dict, blank=True)
    recommended_path = models.CharField(max_length=255, blank=True)
    score = models.IntegerField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.assessment.title} ({'Completed' if self.is_completed else 'In Progress'})"
