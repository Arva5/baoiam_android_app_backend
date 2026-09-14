from django.conf import settings
from django.db import models


class IssueReport(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issue_reports',
    )
    description = models.TextField(help_text="Description of the issue / bug experienced.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Issue Report'
        verbose_name_plural = 'Issue Reports'

    def __str__(self):
        user_email = self.user.email if self.user else "Anonymous"
        return f"Issue #{self.id} by {user_email} ({self.status})"
