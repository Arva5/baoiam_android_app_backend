from django.contrib import admin

from .models import LegalDocument, UserAgreement


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ("doc_type", "version", "title", "is_active", "updated_at")
    list_filter = ("doc_type", "is_active")
    search_fields = ("title", "content", "version")
    readonly_fields = ("created_at", "updated_at")


@admin.register(UserAgreement)
class UserAgreementAdmin(admin.ModelAdmin):
    list_display = ("user_email", "document", "accepted_at")
    list_filter = ("document__doc_type",)
    search_fields = ("user_email",)
    readonly_fields = ("accepted_at",)
