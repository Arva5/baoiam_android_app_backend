import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    ResendOTPSerializer,
    ResetPasswordSerializer,
    SignupSerializer,
    UserSerializer,
    VerifyEmailSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate 6-digit OTP and set 10-minute expiration
        otp = f"{secrets.randbelow(900000) + 100000}"
        user.email_verified = False
        user.email_otp = otp
        user.email_otp_expires_at = timezone.now() + timedelta(minutes=10)
        user.save(update_fields=['email_verified', 'email_otp', 'email_otp_expires_at'])

        # Send OTP email via Django email / Gmail SMTP
        try:
            send_mail(
                subject='Verify Your Email - OTP',
                message=(
                    f"Hello {user.name},\n\n"
                    f"Your 6-digit email verification OTP is: {otp}\n\n"
                    "This code will expire in 10 minutes.\n\n"
                    "Thank you!"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Verify email and clear OTP fields
        user.email_verified = True
        user.email_otp = None
        user.email_otp_expires_at = None
        user.save(update_fields=['email_verified', 'email_otp', 'email_otp_expires_at'])

        return Response({
            'detail': 'Email verified successfully.'
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email__iexact=email)

            if user.email_verified:
                return Response(
                    {'detail': 'Email is already verified.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            now = timezone.now()
            last_sent = user.email_otp_last_sent_at
            if not last_sent and user.email_otp_expires_at:
                inferred_sent = user.email_otp_expires_at - timedelta(minutes=10)
                if inferred_sent <= now:
                    last_sent = inferred_sent

            if last_sent and (now - last_sent) < timedelta(seconds=60):
                seconds_remaining = 60 - int((now - last_sent).total_seconds())
                return Response(
                    {'detail': f'Please wait {seconds_remaining} seconds before requesting a new OTP.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate 6-digit OTP and set 10-minute expiration
            otp = f"{secrets.randbelow(900000) + 100000}"
            user.email_otp = otp
            user.email_otp_expires_at = now + timedelta(minutes=10)
            user.email_otp_last_sent_at = now
            user.save(update_fields=['email_otp', 'email_otp_expires_at', 'email_otp_last_sent_at'])

            # Send OTP email
            try:
                send_mail(
                    subject='Verify Your Email - OTP',
                    message=(
                        f"Hello {user.name},\n\n"
                        f"Your 6-digit email verification OTP is: {otp}\n\n"
                        "This code will expire in 10 minutes.\n\n"
                        "Thank you!"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Failed to send verification email: {e}")

        except User.DoesNotExist:
            pass

        return Response({
            'detail': 'If the email is registered and unverified, a new verification code has been sent.'
        }, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        remember_me = serializer.validated_data.get('remember_me', False)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        if remember_me:
            # Extended token lifetime for remember_me (30 days refresh, 7 days access)
            refresh.set_exp(lifetime=timedelta(days=30))
            access.set_exp(lifetime=timedelta(days=7))

        return Response({
            'access': str(access),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email__iexact=email)
            token = secrets.token_urlsafe(32)
            user.reset_password_token = token
            user.reset_password_token_expires_at = timezone.now() + timedelta(hours=1)
            user.save(update_fields=['reset_password_token', 'reset_password_token_expires_at'])

            # Send password reset email via Django send_mail (Anymail / Resend backend)
            try:
                send_mail(
                    subject='Password Reset Token',
                    message=(
                        f"Hello {user.name},\n\n"
                        "Your password reset token is:\n\n"
                        f"{token}\n\n"
                        "This token will expire in 1 hour.\n\n"
                        "Use this token with the /api/auth/reset-password/ endpoint."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Failed to send password reset email: {e}")
        except User.DoesNotExist:
            pass

        return Response({
            'detail': 'If the email is registered, password reset instructions have been generated.'
        }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        new_password = serializer.validated_data['new_password']

        user.set_password(new_password)
        user.reset_password_token = None
        user.reset_password_token_expires_at = None
        user.save(update_fields=['password', 'reset_password_token', 'reset_password_token_expires_at'])

        return Response({
            'detail': 'Password has been reset successfully.'
        }, status=status.HTTP_200_OK)
