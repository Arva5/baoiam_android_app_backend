from django.conf import settings
from django.db import models


class Certificate(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='certificates'
    )
    badge_icon_url = models.URLField(max_length=500, blank=True, null=True)
    issuer_name = models.CharField(max_length=150, default='Baoiam Learning Platform')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class UserCertificate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    certificate = models.ForeignKey(
        Certificate,
        on_delete=models.CASCADE,
        related_name='issued_certificates'
    )
    certificate_code = models.CharField(max_length=100, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_url = models.URLField(max_length=500, blank=True, null=True)
    is_verified = models.BooleanField(default=True)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f"{self.user} - {self.certificate.title} ({self.certificate_code})"

