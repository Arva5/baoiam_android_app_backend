from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = (
        ('general', 'General'),
        ('course', 'Course'),
        ('announcement', 'Announcement'),
        ('reminder', 'Reminder'),
        ('achievement', 'Achievement'),
        ('promotion', 'Promotion'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        db_index=True,
    )
    title = models.CharField(max_length=255)
    message = models.TextField(help_text='Notification body text.')
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='general',
    )
    action_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Optional deep link or URL to open on click.'
    )
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])
