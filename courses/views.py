from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course
from .serializers import CourseDetailSerializer, CourseListSerializer


class CourseListView(APIView):
    """
    GET /api/courses/
    Public catalogue listing (Home screen). Only published courses are
    shown to non-staff callers. If the caller is authenticated, each course
    includes `is_enrolled` so the app can show "Continue" vs "Enroll".
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Course.objects.all()
        if not (request.user and request.user.is_authenticated and request.user.is_staff):
            qs = qs.filter(is_published=True)
        serializer = CourseListSerializer(qs, many=True, context={"request": request})
        return Response({"success": True, "data": serializer.data})


class CourseDetailView(APIView):
    """
    GET /api/courses/<slug>/
    Course Player payload: curriculum outline is always visible, but lesson
    `content_items` (video/materials URLs) are only included when the
    caller has an ACTIVE, non-expired enrollment - see CourseDetailSerializer.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        if not course.is_published and not (
            request.user and request.user.is_authenticated and request.user.is_staff
        ):
            return Response(
                {"success": False, "errors": ["Course not found."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CourseDetailSerializer(course, context={"request": request})
        return Response({"success": True, "data": serializer.data})
