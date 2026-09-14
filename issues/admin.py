from django.contrib import admin
from .models import IssueReport


@admin.register(IssueReport)
class IssueReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'short_description', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'user__name', 'description', 'admin_notes')
    list_editable = ('status',)

    def user_email(self, obj):
        return obj.user.email if obj.user else "-"
    user_email.short_description = "User Email"

    def short_description(self, obj):
        return obj.description[:80] + "..." if len(obj.description) > 80 else obj.description
    short_description.short_description = "Description"
