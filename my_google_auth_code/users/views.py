from django.conf import settings
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserProfile, OTPVerification, OAuthAccount
from .serializers import (
    SignupEmailSerializer, VerifyOTPSerializer, GoogleAuthSerializer,
    ProfileSetupSerializer, UserSerializer, MeUpdateSerializer,
)
from .utils import (
    hash_otp, verify_otp_hash, send_otp_email, otp_expiry,
    seconds_until_resend_allowed, start_resend_cooldown,
)


def issue_tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class SignupEmailView(APIView):
    """POST /api/auth/signup/email/  { "email": "you@example.com" }
    Generates a 6-digit OTP and emails it asynchronously (prints to console
    in dev). Rate-limited per scope + a short per-email resend cooldown so
    one email address can't be spammed with sends."""
    permission_classes = [AllowAny]
    throttle_scope = "otp_send"

    def post(self, request):
        serializer = SignupEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()

        wait = seconds_until_resend_allowed(email)
        if wait > 0:
            return Response(
                {"success": False, "errors": [f"Please wait {wait}s before requesting another OTP."]},
                status=429,
            )

        otp = OTPVerification.generate_code()
        OTPVerification.objects.create(
            email=email, otp_code_hash=hash_otp(otp), expires_at=otp_expiry()
        )
        send_otp_email(email, otp)
        start_resend_cooldown(email)

        return Response(
            {"success": True, "message": f"OTP sent to {email}", "data": None},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    """POST /api/auth/verify-otp/  { "email": "...", "otp": "123456" }
    Verifies OTP, creates the user if new, and issues JWT tokens."""
    permission_classes = [AllowAny]
    throttle_scope = "otp_verify"

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        otp = serializer.validated_data["otp"]

        record = (
            OTPVerification.objects.filter(email=email, is_verified=False)
            .order_by("-created_at")
            .first()
        )
        if not record:
            return Response({"success": False, "errors": ["No OTP request found. Please request a new one."]}, status=400)
        if record.is_expired():
            return Response({"success": False, "errors": ["OTP expired. Please request a new one."]}, status=400)
        if record.attempt_count >= 5:
            return Response({"success": False, "errors": ["Too many attempts. Please request a new OTP."]}, status=429)
        if not verify_otp_hash(otp, record.otp_code_hash):
            record.attempt_count += 1
            record.save(update_fields=["attempt_count"])
            return Response({"success": False, "errors": ["Incorrect OTP."]}, status=400)

        record.is_verified = True
        record.save(update_fields=["is_verified"])

        user, created = User.objects.get_or_create(
            email=email, defaults={"auth_provider": "email"}
        )
        if not user.is_verified:
            user.is_verified = True
            user.save(update_fields=["is_verified"])
        UserProfile.objects.get_or_create(user=user)

        tokens = issue_tokens_for(user)
        return Response({
            "success": True,
            "data": {
                "tokens": tokens,
                "is_new_user": created,
                "profile_complete": user.profile_complete,
                "user": UserSerializer(user).data,
            },
        })


def _verify_google_id_token(token):
    """Shared helper: verifies a Google id_token server-side and returns the
    decoded payload (email, name, picture, sub, ...). Raises ValueError on
    any problem (bad token, wrong audience, unverified email, etc)."""
    if not settings.GOOGLE_CLIENT_IDS:
        raise ValueError("Google Sign-In is not configured on the server.")

    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests

    idinfo = None
    last_error = None
    # Try each configured client ID; verify_oauth2_token raises if the
    # token's audience doesn't match the one passed in.
    for client_id in settings.GOOGLE_CLIENT_IDS:
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


class GoogleAuthView(APIView):
    """POST /api/auth/google/  { "id_token": "..." }
    Single unified "Continue with Google" endpoint - handles BOTH new and
    existing users with one call, one button on the app side. If no account
    exists for this email, one is created on the fly (as a "student", no
    role selection). If it already exists, we just log them in. The
    response's "is_new_user" flag tells the app whether to route to the
    profile-setup screen or straight to home."""
    permission_classes = [AllowAny]
    throttle_scope = "google_auth"

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            idinfo = _verify_google_id_token(serializer.validated_data["id_token"])
        except Exception as e:
            return Response({"success": False, "errors": [f"Invalid Google token: {e}"]}, status=400)

        email = idinfo.get("email", "").lower()
        google_uid = idinfo.get("sub")
        name = idinfo.get("name", "")
        picture = idinfo.get("picture", "")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name": name,
                "profile_photo_url": picture,
                "auth_provider": "google",
                "is_verified": True,
                "role": "student",  # every signup is a student, no role choice for now
            },
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])

        OAuthAccount.objects.get_or_create(
            provider="google", provider_user_id=google_uid, defaults={"user": user}
        )
        UserProfile.objects.get_or_create(user=user)

        tokens = issue_tokens_for(user)
        return Response({
            "success": True,
            "data": {
                "tokens": tokens,
                "is_new_user": created,
                "profile_complete": user.profile_complete,
                "user": UserSerializer(user).data,
            },
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ProfileSetupView(generics.UpdateAPIView):
    """PATCH /api/auth/profile-setup/  (Authenticated - send access token)"""
    serializer_class = ProfileSetupSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        request.user.refresh_from_db()
        response.data = {"success": True, "data": UserSerializer(request.user).data}
        return response


class MeView(APIView):
    """GET /api/users/me/   PATCH /api/users/me/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"success": True, "data": UserSerializer(request.user).data})

    def patch(self, request):
        serializer = MeUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "data": UserSerializer(request.user).data})


class LogoutView(APIView):
    """POST /api/auth/logout/  { "refresh": "<refresh_token>" } - blacklists it."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh"))
            token.blacklist()
        except Exception as e:
            return Response({"success": False, "errors": [str(e)]}, status=400)
        return Response({"success": True, "message": "Logged out"})
