from django.conf import settings
from django.db import models


class Feedback(models.Model):
    class Experience(models.TextChoices):
        EXCELLENT = "excellent", "Excellent"
        GOOD = "good", "Good"
        OKAY = "okay", "Okay"
        BAD = "bad", "Bad"
        POOR = "poor", "Poor"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedback_submissions",
    )
    rating = models.PositiveSmallIntegerField(
        help_text="Star rating from 1 to 5."
    )
    experience = models.CharField(
        max_length=20,
        choices=Experience.choices,
    )
    feedback = models.TextField(
        blank=True,
        max_length=500,
        help_text="Optional written feedback (max 500 characters).",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    def __str__(self):
        return f"{self.user} — {self.rating}★ ({self.experience})"
