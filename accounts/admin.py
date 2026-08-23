from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'name', 'email_verified', 'is_staff', 'is_active')
    list_filter = ('email_verified', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Email Verification', {'fields': ('email_verified', 'email_otp', 'email_otp_expires_at')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Password Reset', {'fields': ('reset_password_token', 'reset_password_token_expires_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'email_verified'),
        }),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)
