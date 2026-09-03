from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    SignupEmailView, VerifyOTPView, GoogleAuthView,
    ProfileSetupView, MeView, LogoutView,
)

urlpatterns = [
    # ---- Email OTP signup/login — DISABLED for now, only Google is used ----
    # path("auth/signup/email/", SignupEmailView.as_view(), name="signup-email"),
    # path("auth/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),

    # ---- Google Sign-In (only auth method in use right now) ----
    # Single "Continue with Google" endpoint - handles both new and
    # existing users. Frontend just calls this one URL for the button.
    path("auth/google/", GoogleAuthView.as_view(), name="google-auth"),

    path("auth/profile-setup/", ProfileSetupView.as_view(), name="profile-setup"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("users/me/", MeView.as_view(), name="me"),
]
