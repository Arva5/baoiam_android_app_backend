from rest_framework import serializers
from .models import User, UserProfile


class SignupEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)


class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()


class ProfileSetupSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", required=True)
    profile_photo_url = serializers.URLField(source="user.profile_photo_url", required=False, allow_blank=True)

    class Meta:
        model = UserProfile
        fields = [
            "full_name", "profile_photo_url", "courses_interest",
            "highest_qualification", "current_role", "institution",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.profile_complete = True
        instance.user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "username", "profile_photo_url",
            "headline", "role", "auth_provider", "is_verified",
            "profile_complete", "created_at",
        ]
        read_only_fields = fields


class MeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "username", "profile_photo_url", "headline"]
