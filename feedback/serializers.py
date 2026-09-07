from rest_framework import serializers

from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ("id", "rating", "experience", "feedback", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate_feedback(self, value):
        if len(value) > 500:
            raise serializers.ValidationError(
                "Feedback must not exceed 500 characters."
            )
        return value
