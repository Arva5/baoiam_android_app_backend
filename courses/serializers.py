from rest_framework import serializers

from .models import (
    Category,
    ContentItem,
    Course,
    CourseEnrollment,
    CourseModule,
    Lesson,
    PromotionalBanner,
    TipOfTheDay,
    WhyChooseUsItem,
)


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
    Nested inside CourseModuleSerializer. content_items is only populated
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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'icon_url', 'description', 'order', 'is_active')


class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    instructor_name = serializers.CharField(read_only=True)
    total_lectures = serializers.ReadOnlyField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'slug',
            'short_code',
            'subtitle',
            'description',
            'thumbnail_url',
            'cover_image_url',
            'instructor',
            'instructor_name',
            'category',
            'category_name',
            'level',
            'rating',
            'reviews_count',
            'duration_hours',
            'lessons_count',
            'total_lectures',
            'price',
            'discounted_price',
            'is_featured',
            'is_popular',
            'is_published',
            'is_enrolled',
            'created_at',
            'updated_at',
        )

    def get_is_enrolled(self, obj):
        request = self.context.get("request")
        user = request.user if request else None
        if not user or not user.is_authenticated:
            return False
        if obj.course_enrollments.filter(user=user).exists():
            return True
        if hasattr(obj, 'enrollments') and obj.enrollments.filter(user=user).exists():
            return True
        return False



CourseListSerializer = CourseSerializer


class CourseDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    instructor_name = serializers.CharField(read_only=True)
    total_lectures = serializers.ReadOnlyField()
    modules = serializers.SerializerMethodField()
    has_active_access = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'slug',
            'short_code',
            'subtitle',
            'description',
            'thumbnail_url',
            'cover_image_url',
            'instructor',
            'instructor_name',
            'category',
            'category_name',
            'level',
            'rating',
            'reviews_count',
            'duration_hours',
            'lessons_count',
            'total_lectures',
            'price',
            'discounted_price',
            'is_featured',
            'is_popular',
            'is_published',
            'is_enrolled',
            'has_active_access',
            'modules',
            'created_at',
            'updated_at',
        )

    def _has_access(self, obj):
        request = self.context.get("request")
        user = request.user if request else None
        if not user or not user.is_authenticated:
            return False
        if obj.course_enrollments.filter(user=user).exists():
            return True
        if hasattr(obj, 'enrollments') and obj.enrollments.filter(user=user).exists():
            enrollment = obj.enrollments.filter(user=user).first()
            return bool(getattr(enrollment, 'has_active_access', True))
        return False

    def get_is_enrolled(self, obj):
        return self._has_access(obj)

    def get_has_active_access(self, obj):
        return self._has_access(obj)

    def get_modules(self, obj):
        ctx = {"has_access": self._has_access(obj)}
        return CourseModuleSerializer(
            obj.modules.all(), many=True, context=ctx
        ).data


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = (
            'id',
            'course',
            'progress_percentage',
            'completed_lessons',
            'total_lessons',
            'current_lesson_title',
            'is_completed',
            'last_accessed_at',
            'enrolled_at',
        )


class PromotionalBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionalBanner
        fields = (
            'id',
            'title',
            'subtitle',
            'tagline',
            'image_url',
            'badge_text',
            'discount_code',
            'discount_percentage',
            'target_type',
            'target_id',
            'target_url',
            'button_text',
            'start_date',
            'end_date',
            'order',
            'is_active',
        )


class TipOfTheDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = TipOfTheDay
        fields = (
            'id',
            'title',
            'content',
            'category',
            'author_name',
            'author_avatar_url',
            'icon_name',
            'publish_date',
            'likes_count',
            'is_active',
        )


class WhyChooseUsItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhyChooseUsItem
        fields = (
            'id',
            'title',
            'description',
            'icon_url',
            'icon_name',
            'highlight_stat',
            'order',
            'is_active',
        )
