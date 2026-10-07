"""
Staff-only management APIs (backend/admin dashboard ke liye).

Sab endpoints `/api/courses/manage/...` ke neeche hain aur sirf `is_staff=True`
user + Bearer token se chalte hain. Android app inhe use nahi karti.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    ContentItem,
    Course,
    CourseEnrollment,
    CourseModule,
    Lesson,
)

User = get_user_model()

# "Free" = effective price 0 (discounted_price agar hai to wahi, warna price).
FREE_COURSE_Q = Q(discounted_price=0) | Q(discounted_price__isnull=True, price=0)
FREE_ENROLLMENT_Q = Q(course__discounted_price=0) | Q(
    course__discounted_price__isnull=True, course__price=0
)


def _is_free(course):
    price = course.discounted_price if course.discounted_price is not None else course.price
    return price == 0


# --------------------------------------------------------------------------
# Stats
# --------------------------------------------------------------------------

class AdminStatsView(APIView):
    """GET /api/courses/manage/stats/ : users, enrollments, free/paid, per-course counts."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        now = timezone.now()
        enrollments = CourseEnrollment.objects.all()
        free_enrollments = enrollments.filter(FREE_ENROLLMENT_Q)
        paid_enrollments = enrollments.exclude(pk__in=free_enrollments.values("pk"))

        total_users = User.objects.count()
        enrolled_users = enrollments.values("user").distinct().count()
        free_users = free_enrollments.values("user").distinct().count()
        paid_users = paid_enrollments.values("user").distinct().count()

        user_fields = {f.name for f in User._meta.get_fields()}
        new_users_7d = None
        if "date_joined" in user_fields:
            new_users_7d = User.objects.filter(date_joined__gte=now - timedelta(days=7)).count()

        per_course = []
        courses = Course.objects.annotate(
            total_enrollments=Count("course_enrollments", distinct=True),
            completed_count=Count(
                "course_enrollments",
                filter=Q(course_enrollments__is_completed=True),
                distinct=True,
            ),
        ).order_by("-total_enrollments", "title")
        for c in courses:
            per_course.append({
                "id": c.id,
                "title": c.title,
                "slug": c.slug,
                "is_published": c.is_published,
                "is_free": _is_free(c),
                "price": str(c.price),
                "discounted_price": str(c.discounted_price) if c.discounted_price is not None else None,
                "enrollments": c.total_enrollments,
                "completed": c.completed_count,
            })

        data = {
            "users": {
                "total": total_users,
                "with_at_least_one_enrollment": enrolled_users,
                "without_any_enrollment": total_users - enrolled_users,
                "using_free_courses": free_users,
                "using_paid_courses": paid_users,
                "new_last_7_days": new_users_7d,
            },
            "courses": {
                "total": Course.objects.count(),
                "published": Course.objects.filter(is_published=True).count(),
                "unpublished": Course.objects.filter(is_published=False).count(),
                "free": Course.objects.filter(FREE_COURSE_Q).count(),
                "paid": Course.objects.exclude(FREE_COURSE_Q).count(),
            },
            "enrollments": {
                "total": enrollments.count(),
                "free": free_enrollments.count(),
                "paid": paid_enrollments.count(),
                "completed": enrollments.filter(is_completed=True).count(),
                "last_7_days": enrollments.filter(enrolled_at__gte=now - timedelta(days=7)).count(),
                "last_30_days": enrollments.filter(enrolled_at__gte=now - timedelta(days=30)).count(),
            },
            "per_course": per_course,
        }
        return Response(data, status=status.HTTP_200_OK)


# --------------------------------------------------------------------------
# Serializers
# --------------------------------------------------------------------------

class AdminCourseSerializer(serializers.ModelSerializer):
    enrollments_count = serializers.IntegerField(source="course_enrollments.count", read_only=True)
    is_free = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id", "title", "slug", "short_code", "subtitle", "description",
            "thumbnail_url", "cover_image_url",
            "instructor", "instructor_name", "category", "level",
            "rating", "reviews_count", "duration_hours", "lessons_count",
            "price", "discounted_price",
            "is_featured", "is_popular", "is_published",
            "what_you_learn", "key_features",
            "enrollments_count", "is_free",
            "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def get_is_free(self, obj):
        return _is_free(obj)


class AdminModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = ("id", "course", "title", "order", "created_at")
        read_only_fields = ("created_at",)


class AdminLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            "id", "module", "title", "description", "order",
            "thumbnail_url", "is_preview", "video_url", "storage_key",
            "duration_seconds", "published_at", "created_at",
        )
        read_only_fields = ("created_at",)


class AdminContentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentItem
        fields = (
            "id", "lesson", "content_type", "title", "url", "storage_key",
            "duration_seconds", "file_size_bytes", "order", "created_at",
        )
        read_only_fields = ("created_at",)

    def validate(self, attrs):
        # Create pe url ya storage_key me se ek zaroori; update pe purani value bhi gini jaati hai.
        url = attrs.get("url", getattr(self.instance, "url", ""))
        key = attrs.get("storage_key", getattr(self.instance, "storage_key", ""))
        if not (url or key):
            raise serializers.ValidationError("Either 'url' or 'storage_key' is required.")
        return attrs


class AdminEnrollmentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = (
            "id", "user", "user_email", "course", "course_title",
            "progress_percentage", "completed_lessons", "total_lessons",
            "current_lesson_title", "is_completed",
            "last_accessed_at", "enrolled_at",
        )
        read_only_fields = ("last_accessed_at", "enrolled_at")


# --------------------------------------------------------------------------
# ViewSets (list / create / retrieve / update / partial_update / destroy)
# --------------------------------------------------------------------------

class StaffViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]


class AdminCourseViewSet(StaffViewSet):
    """
    /manage/courses/            GET (list, ?search= &is_published= &category=), POST (create)
    /manage/courses/<id>/       GET, PUT, PATCH, DELETE
    """

    serializer_class = AdminCourseSerializer

    def get_queryset(self):
        qs = Course.objects.select_related("category", "instructor").order_by("-created_at")
        p = self.request.query_params
        search = p.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(short_code__icontains=search) | Q(slug__icontains=search)
            )
        if p.get("is_published") is not None:
            qs = qs.filter(is_published=p["is_published"].lower() in ("true", "1", "yes"))
        if p.get("category"):
            qs = qs.filter(category_id=p["category"]) if p["category"].isdigit() else qs.filter(
                category__slug__iexact=p["category"]
            )
        return qs

    def destroy(self, request, *args, **kwargs):
        course = self.get_object()
        count = course.course_enrollments.count()
        force = request.query_params.get("force", "").lower() in ("true", "1", "yes")
        if count and not force:
            return Response(
                {
                    "detail": (
                        f"This course has {count} enrollment(s). Deleting it also deletes all its "
                        "modules, lessons, content and enrollments. Prefer PATCH {\"is_published\": false}, "
                        "or repeat this call with ?force=true to delete anyway."
                    ),
                    "enrollments": count,
                },
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)


class AdminModuleViewSet(StaffViewSet):
    """/manage/modules/  (?course=<id>)"""

    serializer_class = AdminModuleSerializer

    def get_queryset(self):
        qs = CourseModule.objects.all().order_by("course_id", "order")
        course = self.request.query_params.get("course")
        return qs.filter(course_id=course) if course else qs


class AdminLessonViewSet(StaffViewSet):
    """/manage/lessons/  (?module=<id>)"""

    serializer_class = AdminLessonSerializer

    def get_queryset(self):
        qs = Lesson.objects.all().order_by("module_id", "order")
        module = self.request.query_params.get("module")
        return qs.filter(module_id=module) if module else qs


class AdminContentItemViewSet(StaffViewSet):
    """/manage/content-items/  (?lesson=<id>)"""

    serializer_class = AdminContentItemSerializer

    def get_queryset(self):
        qs = ContentItem.objects.all().order_by("lesson_id", "order")
        lesson = self.request.query_params.get("lesson")
        return qs.filter(lesson_id=lesson) if lesson else qs


class AdminEnrollmentViewSet(StaffViewSet):
    """
    /manage/enrollments/   GET (list, ?course= &user= &is_completed=), POST {user, course}
    /manage/enrollments/<id>/   GET, PATCH, DELETE

    POST = user ko course me access dena (paid course ke liye bhi). DELETE = access hatana.
    """

    serializer_class = AdminEnrollmentSerializer

    def get_queryset(self):
        qs = CourseEnrollment.objects.select_related("user", "course").order_by("-enrolled_at")
        p = self.request.query_params
        if p.get("course"):
            qs = qs.filter(course_id=p["course"])
        if p.get("user"):
            qs = qs.filter(user_id=p["user"])
        if p.get("is_completed") is not None:
            qs = qs.filter(is_completed=p["is_completed"].lower() in ("true", "1", "yes"))
        return qs

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        extra = {}
        if not serializer.validated_data.get("total_lessons"):
            extra["total_lessons"] = course.total_lectures
        serializer.save(**extra)
