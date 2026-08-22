from datetime import timedelta
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email')
        read_only_fields = ('id',)


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True)
    agree_to_terms = serializers.BooleanField(required=True)
    class Meta:
        model = User
        fields = ('name', 'email', 'password', 'confirm_password', 'agree_to_terms')

    def validate_email(self, value):
        normalized_email = value.lower()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized_email

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        if not attrs['agree_to_terms']:
            raise serializers.ValidationError({
                "agree_to_terms": "You must agree to the Terms of Use and Privacy Policy."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data.pop('agree_to_terms')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    remember_me = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password')

        # Try authenticating with email as username parameter or keyword argument
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs['user'] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        return value.strip().lower()


class ResetPasswordSerializer(serializers.Serializer):
    reset_token = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        token = attrs.get('reset_token').strip()
        try:
            user = User.objects.get(reset_password_token=token)
        except User.DoesNotExist:
            raise serializers.ValidationError({"reset_token": "Invalid or expired reset token."})

        if not user.reset_password_token_expires_at or user.reset_password_token_expires_at < timezone.now():
            raise serializers.ValidationError({"reset_token": "Invalid or expired reset token."})

        attrs['user'] = user
        return attrs
