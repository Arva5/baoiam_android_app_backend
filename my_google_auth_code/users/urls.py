from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    SignupEmailView, VerifyOTPView, GoogleSignupView, GoogleLoginView,
    ProfileSetupView, MeView, LogoutView,
)

urlpatterns = [
    # ---- Email OTP signup/login — DISABLED for now, only Google is used ----
    # path("auth/signup/email/", SignupEmailView.as_view(), name="signup-email"),
    # path("auth/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),

    # ---- Google Sign-In (only auth method in use right now) ----
    path("auth/google/signup/", GoogleSignupView.as_view(), name="google-signup"),
    path("auth/google/login/", GoogleLoginView.as_view(), name="google-login"),

    path("auth/profile-setup/", ProfileSetupView.as_view(), name="profile-setup"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("users/me/", MeView.as_view(), name="me"),
]
