from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Enrollment
from .serializers import EnrollmentSerializer, EnrollSerializer


class EnrollmentListCreateView(APIView):
    """
    GET  /api/enrollments/   -> the logged-in user's "Enrolled Courses"
                                 list (My Learning / Recordings screen).
    POST /api/enrollments/   -> enroll the logged-in user in a course.
                                 Body: { "course_slug": "ui-ux-design" }
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Enrollment.objects.filter(user=request.user).select_related("course")
        serializer = EnrollmentSerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})

    def post(self, request):
        serializer = EnrollSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save()
        return Response(
            {"success": True, "data": EnrollmentSerializer(enrollment).data},
            status=status.HTTP_201_CREATED,
        )


class EnrollmentDetailView(APIView):
    """
    GET /api/enrollments/<course_slug>/
    Single enrollment lookup - used by the app to check
    "does this user have active access to this specific course?"
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, course_slug):
        enrollment = Enrollment.objects.filter(
            user=request.user, course__slug=course_slug
        ).select_related("course").first()
        if enrollment is None:
            return Response(
                {"success": False, "errors": ["You are not enrolled in this course."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"success": True, "data": EnrollmentSerializer(enrollment).data})
