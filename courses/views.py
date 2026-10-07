from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Category,
    ContentItem,
    Course,
    CourseBookmark,
    CourseEnrollment,
    PromotionalBanner,
    TipOfTheDay,
    WhyChooseUsItem,
)
from .serializers import (
    CategorySerializer,
    CourseBookmarkSerializer,
    CourseDetailSerializer,
    CourseEnrollmentSerializer,
    CourseListSerializer,
    PromotionalBannerSerializer,
    TipOfTheDaySerializer,
    WhyChooseUsItemSerializer,
    user_has_course_access,
)
from .storage import mime_type_for, resolve_playback_url


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True).order_by('order', 'name')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class CourseListView(generics.ListAPIView):
    """
    GET /courses/  -> courses + modules/lessons/content_items (video url) .
    Video links sirf enrolled user ko; `?include_modules=false` se halka list.
    """
    serializer_class = CourseListSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        flag = self.request.query_params.get('include_modules', 'true').lower()
        ctx['include_modules'] = flag not in ('false', '0', 'no')
        return ctx

    def get_queryset(self):
        user = self.request.user
        include_drafts = self.request.query_params.get('include_drafts')
        if include_drafts is not None and include_drafts.lower() in ('true', '1', 'yes'):
            queryset = Course.objects.all()
        elif user and user.is_authenticated and user.is_staff:
            queryset = Course.objects.all()
        else:
            queryset = Course.objects.filter(is_published=True)

        search_query = self.request.query_params.get('search') or self.request.query_params.get('q')
        category_param = self.request.query_params.get('category') or self.request.query_params.get('category_id')
        is_featured = self.request.query_params.get('is_featured')
        level = self.request.query_params.get('level')

        if search_query:
            search_query = search_query.strip()
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(subtitle__icontains=search_query) |
                Q(short_code__icontains=search_query) |
                Q(instructor_name__icontains=search_query) |
                Q(instructor__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        if category_param:
            if str(category_param).isdigit():
                queryset = queryset.filter(
                    Q(category_id=int(category_param)) | Q(category__slug__iexact=str(category_param))
                )
            else:
                queryset = queryset.filter(
                    Q(category__slug__iexact=category_param) | Q(category__name__iexact=category_param)
                )
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured.lower() == 'true')
        if level:
            queryset = queryset.filter(level=level)

        return queryset.select_related('category', 'instructor').prefetch_related(
            'modules__lessons__content_items'
        )


class ContentPlayView(APIView):
    """
    GET /api/courses/content/<id>/play/
    Enrolled user ko playable Cloudflare/sample video URL deta hai.
    Android isi `url` ko player me lagata hai.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        item = get_object_or_404(
            ContentItem.objects.select_related("lesson__module__course"),
            id=id,
        )
        course = item.lesson.module.course
        if not user_has_course_access(request, course):
            return Response(
                {"detail": "Enroll in this course to play this content."},
                status=status.HTTP_403_FORBIDDEN,
            )
        url = resolve_playback_url(item)
        if not url:
            return Response(
                {"detail": "No playback URL configured for this item."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "content_id": item.id,
                "lesson_id": item.lesson_id,
                "course_id": course.id,
                "course_slug": course.slug,
                "content_type": item.content_type,
                "title": item.title,
                "url": url,
                "play_url": url,
                "mime_type": mime_type_for(item),
                "duration_seconds": item.duration_seconds,
                "duration_display": item.duration_display,
            },
            status=status.HTTP_200_OK,
        )


class CourseEnrollView(APIView):
    """
    POST /courses/<id or slug>/enroll/   (body nahi chahiye, Bearer token chahiye)
    FREE course me enroll karta hai. Paid course pe 402 (payment flow alag se banega).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        lookup = kwargs.get('slug') or kwargs.get('id')
        qs = Course.objects.filter(is_published=True)
        course = get_object_or_404(qs, id=int(lookup)) if str(lookup).isdigit() else get_object_or_404(qs, slug=lookup)

        effective_price = course.discounted_price if course.discounted_price is not None else course.price
        if effective_price and effective_price > 0:
            return Response(
                {"detail": "Payment required for this course."},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=request.user, course=course,
            defaults={'total_lessons': course.total_lectures},
        )
        data = CourseEnrollmentSerializer(enrollment, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class CourseDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        lookup = kwargs.get('slug') or kwargs.get('id')
        base_qs = Course.objects.select_related('category', 'instructor')
        if isinstance(lookup, int) or (isinstance(lookup, str) and lookup.isdigit()):
            course = get_object_or_404(base_qs, id=int(lookup))
        else:
            course = get_object_or_404(base_qs, slug=lookup)

        if not course.is_published and not (
            (request.user and request.user.is_authenticated and request.user.is_staff)
            or request.query_params.get("include_drafts", "").lower() in ("true", "1")
            or request.query_params.get("preview", "").lower() in ("true", "1")
        ):
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CourseDetailSerializer(course, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PromotionalBannerListView(generics.ListAPIView):
    serializer_class = PromotionalBannerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        now = timezone.now()
        return PromotionalBanner.objects.filter(
            is_active=True
        ).exclude(
            start_date__gt=now
        ).exclude(
            end_date__lt=now
        ).order_by('order', '-created_at')


class TipOfTheDayView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        today = timezone.localdate()
        tip = TipOfTheDay.objects.filter(
            is_active=True,
            publish_date=today
        ).first()

        if not tip:
            tip = TipOfTheDay.objects.filter(is_active=True).first()

        if not tip:
            return Response(
                {"detail": "No tip of the day found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(TipOfTheDaySerializer(tip).data, status=status.HTTP_200_OK)


class WhyChooseUsListView(generics.ListAPIView):
    queryset = WhyChooseUsItem.objects.filter(is_active=True).order_by('order')
    serializer_class = WhyChooseUsItemSerializer
    permission_classes = [AllowAny]


class UserEnrollmentListView(generics.ListAPIView):
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CourseEnrollment.objects.filter(user=self.request.user).select_related('course')


class LessonPlayView(APIView):
    """
    GET /api/courses/lessons/<id>/play/
    Returns playable Cloudflare URL for this lecture.
    Preview lectures are playable even for non-enrolled users!
    """
    permission_classes = [AllowAny]

    def get(self, request, id):
        from .models import Lesson
        lesson = get_object_or_404(
            Lesson.objects.select_related("module__course"),
            id=id,
        )
        course = lesson.module.course
        has_access = user_has_course_access(request, course)
        if not has_access and not lesson.is_preview:
            return Response(
                {"detail": "Enroll in this course to play this lecture."},
                status=status.HTTP_403_FORBIDDEN,
            )
        url = lesson.get_playback_url()
        if not url:
            return Response(
                {"detail": "No playback URL configured for this lecture."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "lesson_id": lesson.id,
                "module_id": lesson.module_id,
                "course_id": course.id,
                "course_slug": course.slug,
                "title": lesson.title,
                "url": url,
                "play_url": url,
                "mime_type": "video/mp4",
                "duration_seconds": lesson.duration_seconds,
                "duration_display": lesson.duration_display,
                "is_preview": lesson.is_preview,
            },
            status=status.HTTP_200_OK,
        )


class CourseSaveView(APIView):
    """
    POST /api/courses/<id>/save/   -> Bookmark / Save course
    DELETE /api/courses/<id>/save/ -> Remove Bookmark
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        lookup = kwargs.get('slug') or kwargs.get('id')
        qs = Course.objects.all()
        course = get_object_or_404(qs, id=int(lookup)) if str(lookup).isdigit() else get_object_or_404(qs, slug=lookup)
        bookmark, created = CourseBookmark.objects.get_or_create(user=request.user, course=course)
        return Response(
            {
                "is_saved": True,
                "course_id": course.id,
                "message": "Course saved successfully." if created else "Course already saved."
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    def delete(self, request, *args, **kwargs):
        lookup = kwargs.get('slug') or kwargs.get('id')
        qs = Course.objects.all()
        course = get_object_or_404(qs, id=int(lookup)) if str(lookup).isdigit() else get_object_or_404(qs, slug=lookup)
        deleted_count, _ = CourseBookmark.objects.filter(user=request.user, course=course).delete()
        return Response(
            {
                "is_saved": False,
                "course_id": course.id,
                "message": "Course removed from bookmarks." if deleted_count else "Course was not bookmarked."
            },
            status=status.HTTP_200_OK
        )


class SavedCoursesListView(generics.ListAPIView):
    """
    GET /api/courses/saved/ -> List of courses bookmarked by the user
    """
    serializer_class = CourseBookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CourseBookmark.objects.filter(user=self.request.user).select_related('course', 'course__category')