from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "rating", "experience", "created_at")
    list_filter = ("rating", "experience", "created_at")
    search_fields = ("user__email", "feedback")
    readonly_fields = ("user", "rating", "experience", "feedback", "created_at")
    ordering = ("-created_at",)
