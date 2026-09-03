from django.conf import settings
from django.db import models
from django.utils import timezone


class Enrollment(models.Model):
    """
    Links a user to a course they've enrolled in. This is the single
    source of truth for:
      - Home screen: "no enrollment -> show Home, don't show My Learning content"
      - MyLearning / Recordings screen: "Enrolled Courses" list
      - Access control: has this user paid for / been granted this course?
    """

    class Status(models.TextChoices):
        PENDING_PAYMENT = "PENDING_PAYMENT", "Pending Payment"
        ACTIVE = "ACTIVE", "Active"
        EXPIRED = "EXPIRED", "Expired"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE,
        help_text="PENDING_PAYMENT until Commerce/Payment (Phase 10) marks it ACTIVE.",
    )

    enrolled_at = models.DateTimeField(default=timezone.now)
    access_expires_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Null = lifetime access. Set this for time-limited course access.",
    )

    class Meta:
        unique_together = ("user", "course")
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.user} -> {self.course} ({self.status})"

    @property
    def has_active_access(self):
        if self.status != self.Status.ACTIVE:
            return False
        if self.access_expires_at and self.access_expires_at < timezone.now():
            return False
        return True
