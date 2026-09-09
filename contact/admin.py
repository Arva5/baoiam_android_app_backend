from django.contrib import admin
from .models import ContactMessage, ContactSupportChannel, PopularQuestion


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(ContactSupportChannel)
class ContactSupportChannelAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel_type', 'subtitle', 'value', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    search_fields = ('title', 'subtitle', 'value')


@admin.register(PopularQuestion)
class PopularQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    search_fields = ('question', 'answer', 'category')
