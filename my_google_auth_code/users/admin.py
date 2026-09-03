from django.contrib import admin
from .models import User, UserProfile, OTPVerification, OAuthAccount


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name", "role", "auth_provider", "is_verified", "profile_complete", "created_at")
    search_fields = ("email", "full_name")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "current_role", "institution")


@admin.register(OTPVerification)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("email", "purpose", "is_verified", "attempt_count", "expires_at", "created_at")


@admin.register(OAuthAccount)
class OAuthAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "provider_user_id", "linked_at")
