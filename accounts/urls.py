from django.urls import path
from .views import (
    CurrentUserView,
    ForgotPasswordView,
    LoginView,
    ResendOTPView,
    ResetPasswordView,
    SignupView,
    VerifyEmailView,
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
]
