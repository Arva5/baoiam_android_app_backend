from django.db import models


class LegalDocument(models.Model):
    """
    A single legal document (Terms & Conditions, Privacy Policy, etc).
    Company edits the content from Django admin - the app/frontend always
    fetches the latest ACTIVE version via the API, so nothing is hardcoded
    on the client. Old versions are kept (is_active=False) for history /
    audit, and to know exactly what a user agreed to at signup time.
    """

    DOC_TYPE_CHOICES = (
        ("terms", "Terms & Conditions"),
        ("privacy", "Privacy Policy"),
    )

    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES)
    version = models.CharField(
        max_length=20,
        help_text="e.g. '1.0', '2026-08-26'. Shown to the app so it can detect changes.",
    )
    title = models.CharField(max_length=255)
    content = models.TextField(
        help_text="Full document body. Markdown is fine if your app renders it; plain text also works."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only one active document per doc_type should exist at a time.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # Enforce "only one active version per type": activating this one
        # deactivates any other active document of the same type.
        if self.is_active:
            LegalDocument.objects.filter(
                doc_type=self.doc_type, is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_doc_type_display()} v{self.version} ({'active' if self.is_active else 'archived'})"


class UserAgreement(models.Model):
    """
    Records that a specific user accepted a specific version of a legal
    document (e.g. at signup). Keeps an auditable trail - useful if a
    dispute ever comes up about what the user agreed to and when.
    """

    # Loose email reference (not a real ForeignKey) so this app doesn't need
    # to depend on which User model (accounts.User vs
    # my_google_auth_code.users.User) accepted it - both flows can log here.
    user_email = models.EmailField()
    document = models.ForeignKey(
        LegalDocument, on_delete=models.PROTECT, related_name="agreements"
    )
    accepted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_email} accepted {self.document}"
