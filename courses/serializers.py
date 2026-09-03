from rest_framework import serializers

from .models import ContentItem, Course, CourseModule, Lesson


class ContentItemSerializer(serializers.ModelSerializer):
    duration_display = serializers.ReadOnlyField()

    class Meta:
        model = ContentItem
        fields = [
            "id", "content_type", "title", "url",
            "duration_seconds", "duration_display",
            "file_size_bytes", "order",
        ]


class LessonSerializer(serializers.ModelSerializer):
    """
    Nested inside CourseModuleSerializer. `content_items` is only populated
    when the requesting user has active access to the course (see
    CourseDetailView) - otherwise lessons show as locked previews.
    """

    content_items = serializers.SerializerMethodField()
    locked = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ["id", "title", "order", "published_at", "locked", "content_items"]

    def get_locked(self, obj):
        return not self.context.get("has_access", False)

    def get_content_items(self, obj):
        if not self.context.get("has_access", False):
            return []
        return ContentItemSerializer(obj.content_items.all(), many=True).data


class CourseModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = CourseModule
        fields = ["id", "title", "order", "lessons"]


class CourseListSerializer(serializers.ModelSerializer):
    """Used for GET /api/courses/ - the course catalogue / Home screen list."""

    instructor_name = serializers.CharField(source="instructor.name", read_only=True, default=None)
    total_lectures = serializers.ReadOnlyField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id", "title", "slug", "short_code", "thumbnail_url",
            "instructor_name", "total_lectures", "is_published",
            "is_enrolled", "created_at",
        ]

    def get_is_enrolled(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if not user or not user.is_authenticated:
            return False
        return obj.enrollments.filter(user=user).exists()


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Used for GET /api/courses/<slug>/ - full Course Player payload.
    `has_active_access` tells the app whether to render locked or unlocked
    lesson content; `modules` is always present so the curriculum outline
    (module/lecture titles + counts) is visible even before enrolling.
    """

    instructor_name = serializers.CharField(source="instructor.name", read_only=True, default=None)
    total_lectures = serializers.ReadOnlyField()
    modules = serializers.SerializerMethodField()
    has_active_access = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id", "title", "slug", "short_code", "description", "thumbnail_url",
            "instructor_name", "total_lectures", "is_published",
            "has_active_access", "modules", "created_at",
        ]

    def _has_access(self, obj):
        request = self.context.get("request")
        user = request.user if request else None
        if not user or not user.is_authenticated:
            return False
        enrollment = obj.enrollments.filter(user=user).first()
        return bool(enrollment and enrollment.has_active_access)

    def get_has_active_access(self, obj):
        return self._has_access(obj)

    def get_modules(self, obj):
        ctx = {"has_access": self._has_access(obj)}
        return CourseModuleSerializer(
            obj.modules.all(), many=True, context=ctx
        ).data
