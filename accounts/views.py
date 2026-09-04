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

from .models import UserProfile, OAuthAccount
from .serializers import (
    DeleteAccountSerializer,
    ForgotPasswordSerializer,
    GoogleAuthSerializer,
    LoginSerializer,
    LogoutSerializer,
    ProfileSetupSerializer,
    ResendOTPSerializer,
    ResetPasswordSerializer,
    SignupSerializer,
    UserProfileSerializer,
    UserSerializer,
    VerifyEmailSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()


def _verify_google_id_token(token):
    """
    Verifies a Google id_token server-side and returns decoded payload.
    Validates token audience against settings.GOOGLE_CLIENT_IDS.
    """
    client_ids = getattr(settings, 'GOOGLE_CLIENT_IDS', [])
    if not client_ids:
        single_cid = getattr(settings, 'GOOGLE_CLIENT_ID', '')
        if single_cid:
            client_ids = [single_cid]

    if not client_ids:
        raise ValueError("Google Sign-In is not configured on the server.")

    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests

    idinfo = None
    last_error = None
    for client_id in client_ids:
        try:
            idinfo = google_id_token.verify_oauth2_token(
                token, google_requests.Request(), client_id
            )
            break
        except ValueError as e:
            last_error = e
            continue

    if idinfo is None:
        raise last_error or ValueError("Invalid token audience")

    if idinfo.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise ValueError("Invalid issuer")
    if not idinfo.get("email_verified", False):
        raise ValueError("Google account email is not verified.")
    return idinfo


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

        # Send OTP email via configured email backend (Resend Anymail)
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


class GoogleAuthView(APIView):
    """
    POST /api/auth/google/ { "id_token": "..." }
    Unified Google Sign-In / Sign-Up endpoint using authoritative accounts.User model.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            idinfo = _verify_google_id_token(serializer.validated_data["id_token"])
        except Exception as e:
            return Response(
                {"success": False, "errors": [f"Invalid Google token: {e}"], "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = idinfo.get("email", "").lower().strip()
        google_uid = idinfo.get("sub")
        name = idinfo.get("name", "").strip()
        picture = idinfo.get("picture", "")

        user = User.objects.filter(email__iexact=email).first()
        created = False

        if not user:
            user = User.objects.create_user(
                email=email,
                name=name or email.split('@')[0],
                email_verified=True,
            )
            user.set_unusable_password()
            user.save()
            created = True
        else:
            if not user.email_verified:
                user.email_verified = True
                user.save(update_fields=["email_verified"])
            if not user.name and name:
                user.name = name
                user.save(update_fields=["name"])

        # Link OAuthAccount
        OAuthAccount.objects.get_or_create(
            provider="google",
            provider_user_id=google_uid,
            defaults={"user": user}
        )

        # Ensure profile exists
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if picture and not profile.avatar_url:
            profile.avatar_url = picture
            profile.save(update_fields=["avatar_url"])

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
            "success": True,
            "access": str(access),
            "refresh": str(refresh),
            "data": {
                "access": str(access),
                "refresh": str(refresh),
                "tokens": {
                    "access": str(access),
                    "refresh": str(refresh)
                },
                "is_new_user": created,
                "profile_complete": profile.is_profile_completed,
                "user": UserSerializer(user).data,
            }
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class LogoutView(APIView):
    """
    POST /api/auth/logout/ { "refresh": "<refresh_token>" }
    Blacklists the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except Exception as e:
            return Response({"success": False, "detail": str(e), "errors": [str(e)]}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success": True, "message": "Logged out successfully.", "detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']

        if not request.user.check_password(password):
            return Response(
                {'detail': 'Incorrect password.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.delete()

        return Response({
            'detail': 'Account deleted successfully.'
        }, status=status.HTTP_200_OK)


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


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileSetupView(APIView):
    """
    PATCH /api/auth/profile-setup/
    Dedicated endpoint for profile setup flow.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = ProfileSetupSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "success": True,
            "data": UserProfileSerializer(profile).data,
            "profile_complete": profile.is_profile_completed,
        }, status=status.HTTP_200_OK)

