from rest_framework import serializers

from courses.models import Course

from .models import Enrollment


class EnrollmentCourseSerializer(serializers.ModelSerializer):
    """Lightweight nested course info for the 'Enrolled Courses' list."""

    total_lectures = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = ["id", "title", "slug", "short_code", "thumbnail_url", "total_lectures"]


class EnrollmentSerializer(serializers.ModelSerializer):
    course = EnrollmentCourseSerializer(read_only=True)
    has_active_access = serializers.ReadOnlyField()

    class Meta:
        model = Enrollment
        fields = [
            "id", "course", "status", "enrolled_at",
            "access_expires_at", "has_active_access",
        ]
        read_only_fields = fields


class EnrollSerializer(serializers.Serializer):
    """POST body for creating an enrollment: { "course_slug": "ui-ux-design" }"""

    course_slug = serializers.SlugField()

    def validate_course_slug(self, value):
        try:
            course = Course.objects.get(slug=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError("No course found with this slug.")
        if not course.is_published:
            raise serializers.ValidationError("This course is not available for enrollment.")
        self.context["course"] = course
        return value

    def validate(self, attrs):
        request = self.context["request"]
        course = self.context["course"]
        if Enrollment.objects.filter(user=request.user, course=course).exists():
            raise serializers.ValidationError(
                {"course_slug": "You are already enrolled in this course."}
            )
        return attrs

    def create(self, validated_data):
        return Enrollment.objects.create(
            user=self.context["request"].user,
            course=self.context["course"],
        )
