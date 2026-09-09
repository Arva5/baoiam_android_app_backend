from django.conf import settings
from django.db import models


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_messages',
    )
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.status})"


class ContactSupportChannel(models.Model):
    CHANNEL_TYPES = [
        ('live_chat', 'Live Chat'),
        ('call', 'Call Us'),
        ('email', 'Email'),
        ('other', 'Other'),
    ]

    channel_type = models.CharField(
        max_length=50,
        choices=CHANNEL_TYPES,
        default='other',
    )
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    value = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Support Channel'
        verbose_name_plural = 'Support Channels'

    def __str__(self):
        return self.title


class PopularQuestion(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Popular Question'
        verbose_name_plural = 'Popular Questions'

    def __str__(self):
        return self.question
