import random
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, full_name="", password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # OTP / Google users don't need a password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name="", password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("profile_complete", True)
        return self.create_user(email, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    AUTH_PROVIDER_CHOICES = (("email", "Email OTP"), ("google", "Google"))
    ROLE_CHOICES = (("student", "Student"), ("instructor", "Instructor"), ("admin", "Admin"))

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150, blank=True)
    username = models.CharField(max_length=150, blank=True)  # display handle, not login field
    profile_photo_url = models.URLField(blank=True, null=True)
    headline = models.CharField(max_length=255, blank=True)  # e.g. "UX Design Lead"
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    auth_provider = models.CharField(max_length=20, choices=AUTH_PROVIDER_CHOICES, default="email")

    is_verified = models.BooleanField(default=False)     # email OTP verified at least once
    profile_complete = models.BooleanField(default=False)  # profile setup screen done
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

   
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="users_app_users",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="users_app_users_permissions",
        blank=True,
    )
    objects = UserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    current_role = models.CharField(max_length=150, blank=True)
    institution = models.CharField(max_length=255, blank=True)
    highest_qualification = models.CharField(max_length=150, blank=True)
    courses_interest = models.CharField(max_length=255, blank=True)  # comma separated, simple v1
    skills = models.JSONField(default=list, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    language = models.CharField(max_length=50, default="English")
    timezone = models.CharField(max_length=50, default="Asia/Kolkata")
    notifications_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Profile<{self.user.email}>"


class OTPVerification(models.Model):
    email = models.EmailField(db_index=True)
    otp_code_hash = models.CharField(max_length=128)
    purpose = models.CharField(max_length=30, default="signup")  # signup / login
    expires_at = models.DateTimeField()
    attempt_count = models.PositiveSmallIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    @staticmethod
    def generate_code():
        # 6 digits (1M combinations) instead of 4 (10K) - much harder to
        # bruteforce even with the attempt/rate limits in place.
        return f"{random.SystemRandom().randint(0, 999999):06d}"


class OAuthAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="oauth_accounts")
    provider = models.CharField(max_length=20, default="google")
    provider_user_id = models.CharField(max_length=255)
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("provider", "provider_user_id")
