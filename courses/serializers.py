from rest_framework import serializers

from .storage import resolve_playback_url
from .models import (
    Category,
    ContentItem,
    Course,
    CourseBookmark,
    CourseEnrollment,
    CourseModule,
    Lesson,
    PromotionalBanner,
    TipOfTheDay,
    WhyChooseUsItem,
)


class ContentItemSerializer(serializers.ModelSerializer):
    duration_display = serializers.ReadOnlyField()
    url = serializers.SerializerMethodField()
    play_url = serializers.SerializerMethodField()

    class Meta:
        model = ContentItem
        fields = [
            "id", "content_type", "title", "url", "play_url",
            "duration_seconds", "duration_display",
            "file_size_bytes", "order",
        ]

    def get_url(self, obj):
        return resolve_playback_url(obj)

    def get_play_url(self, obj):
        return resolve_playback_url(obj)


class LessonSerializer(serializers.ModelSerializer):
    """
    Nested inside CourseModuleSerializer. Provides lecture info including
    video_url for preview or enrolled users, duration formatted, and content items.
    """
    duration = serializers.CharField(source='duration_display', read_only=True)
    video_url = serializers.SerializerMethodField()
    locked = serializers.SerializerMethodField()
    content_items = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "description",
            "order",
            "duration",
            "duration_seconds",
            "video_url",
            "thumbnail_url",
            "is_preview",
            "locked",
            "published_at",
            "content_items",
        ]

    def get_locked(self, obj):
        has_access = self.context.get("has_access", False)
        if has_access:
            return False
        return not obj.is_preview

    def get_video_url(self, obj):
        has_access = self.context.get("has_access", False)
        if has_access or obj.is_preview:
            return obj.get_playback_url()
        return None

    def get_content_items(self, obj):
        has_access = self.context.get("has_access", False)
        if not has_access and not obj.is_preview:
            return []
        return ContentItemSerializer(obj.content_items.all(), many=True).data


class CourseModuleSerializer(serializers.ModelSerializer):
    lectures = serializers.SerializerMethodField()
    

    class Meta:
        model = CourseModule
        fields = ["id", "title", "order", "lectures", "lessons"]

    def get_lectures(self, obj):
        return LessonSerializer(obj.lessons.all(), many=True, context=self.context).data



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'icon_url', 'description', 'order', 'is_active')


class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    instructor_name = serializers.CharField(read_only=True)
    total_lectures = serializers.ReadOnlyField()
    is_enrolled = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

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
            'is_saved',
            'what_you_learn',
            'key_features',
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

    def get_is_saved(self, obj):
        request = self.context.get("request")
        user = request.user if request else None
        if not user or not user.is_authenticated:
            return False
        return obj.bookmarks.filter(user=user).exists()


def user_has_course_access(request, course):
    """Same access rule jo CourseDetailSerializer pehle use karta tha (ab shared)."""
    user = request.user if request else None
    if not user or not user.is_authenticated:
        return False
    if course.course_enrollments.filter(user=user).exists():
        return True
    if hasattr(course, 'enrollments') and course.enrollments.filter(user=user).exists():
        enrollment = course.enrollments.filter(user=user).first()
        return bool(getattr(enrollment, 'has_active_access', True))
    return False


class CourseListSerializer(CourseSerializer):
    """
    GET /courses/ ke liye: CourseSerializer + modules -> lessons -> content_items (video links).
    Content sirf enrolled user ko milta hai, baaki ko lessons `locked: true` aur content_items [] aate hain.
    `?include_modules=false` se modules hataye ja sakte hain (halka payload).
    """

    modules = serializers.SerializerMethodField()

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ('has_active_access', 'modules')

    has_active_access = serializers.SerializerMethodField()

    def get_has_active_access(self, obj):
        return user_has_course_access(self.context.get("request"), obj)

    def get_modules(self, obj):
        if self.context.get("include_modules", True) is False:
            return []
        ctx = {"has_access": self.get_has_active_access(obj)}
        return CourseModuleSerializer(obj.modules.all(), many=True, context=ctx).data


class CourseDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    instructor_name = serializers.CharField(read_only=True)
    total_lectures = serializers.ReadOnlyField()
    modules = serializers.SerializerMethodField()
    has_active_access = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

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
            'is_saved',
            'what_you_learn',
            'key_features',
            'has_active_access',
            'modules',
            'created_at',
            'updated_at',
        )

    def _has_access(self, obj):
        return user_has_course_access(self.context.get("request"), obj)

    def get_is_enrolled(self, obj):
        return self._has_access(obj)

    def get_is_saved(self, obj):
        request = self.context.get("request")
        user = request.user if request else None
        if not user or not user.is_authenticated:
            return False
        return obj.bookmarks.filter(user=user).exists()

    def get_has_active_access(self, obj):
        return self._has_access(obj)

    def get_modules(self, obj):
        ctx = {"has_access": self._has_access(obj)}
        return CourseModuleSerializer(
            obj.modules.all(), many=True, context=ctx
        ).data


class CourseBookmarkSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = CourseBookmark
        fields = ('id', 'course', 'created_at')


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