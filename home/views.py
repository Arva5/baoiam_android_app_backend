from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import (
    GettingStartedSerializer,
    HomeScreenEngagementSerializer,
    LearningPathQuizHomeSerializer,
    NotificationSerializer,
    PromotionalBannerHomeSerializer,
    StartYourJourneyHomeSerializer,
    TipOfTheDayHomeSerializer,
    WhyChooseUsHomeSerializer,
)
from .services import (
    get_getting_started_data,
    get_home_screen_1_engagement,
    get_learning_path_quiz_data,
    get_promotional_banners_data,
    get_start_your_journey_data,
    get_tip_of_the_day_data,
    get_why_choose_us_data,
)


class HomeScreenEngagementView(APIView):
    """
    Main Aggregated API for Home Screen 1: Engagement Content.
    Returns:
      1. Getting Started
      2. Promotional Banner
      3. Learning Path Quiz
      4. Why Choose Us
      5. Tip of the Day
      6. Start Your Journey
    Supports both authenticated and guest users.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        data = get_home_screen_1_engagement(user)
        serializer = HomeScreenEngagementSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GettingStartedView(APIView):
    """
    Returns user onboarding status and getting started steps.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        data = get_getting_started_data(user)
        serializer = GettingStartedSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PromotionalBannersView(APIView):
    """
    Returns promotional banners and special discount offers for Home Screen 1.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        data = get_promotional_banners_data()
        serializer = PromotionalBannerHomeSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LearningPathQuizView(APIView):
    """
    Returns featured Learning Path Quiz details and user completion status.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        data = get_learning_path_quiz_data(user)
        serializer = LearningPathQuizHomeSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WhyChooseUsView(APIView):
    """
    Returns 'Why Choose Us' value propositions and key highlights.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        data = get_why_choose_us_data()
        serializer = WhyChooseUsHomeSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TipOfTheDayView(APIView):
    """
    Returns today's learning tip or latest active tip.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        data = get_tip_of_the_day_data()
        if not data:
            return Response(
                {"detail": "No tip of the day found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TipOfTheDayHomeSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StartYourJourneyView(APIView):
    """
    Returns user's learning progress, resume course, certificates earned, and next milestones.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        data = get_start_your_journey_data(user)
        serializer = StartYourJourneyHomeSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationListView(generics.ListAPIView):
    """
    Returns list of notifications for the authenticated user.
    Supports filtering:
      - ?unread=true (or ?unread=false)
      - ?type=course (or ?notification_type=general)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)

        unread_param = self.request.query_params.get('unread')
        if unread_param is not None:
            if unread_param.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(is_read=False)
            elif unread_param.lower() in ['false', '0', 'no']:
                queryset = queryset.filter(is_read=True)

        is_read_param = self.request.query_params.get('is_read')
        if is_read_param is not None:
            if is_read_param.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(is_read=True)
            elif is_read_param.lower() in ['false', '0', 'no']:
                queryset = queryset.filter(is_read=False)

        notification_type = (
            self.request.query_params.get('type')
            or self.request.query_params.get('notification_type')
        )
        if notification_type:
            queryset = queryset.filter(notification_type__iexact=notification_type)

        return queryset


class NotificationMarkReadView(APIView):
    """
    Marks a single notification as read for the authenticated user.
    Accessible via POST or PATCH /api/home/notifications/<pk>/read/ (or /api/home/notifications/<pk>/).
    """
    permission_classes = [IsAuthenticated]

    def _mark_read(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, user=request.user)
        notification.mark_as_read()
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk, *args, **kwargs):
        return self._mark_read(request, pk)

    def patch(self, request, pk, *args, **kwargs):
        return self._mark_read(request, pk)

    def put(self, request, pk, *args, **kwargs):
        return self._mark_read(request, pk)


class NotificationMarkAllReadView(APIView):
    """
    Marks all unread notifications for the authenticated user as read.
    POST /api/home/notifications/mark-all-read/ or /api/home/notifications/read-all/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        now = timezone.now()
        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(
            is_read=True,
            read_at=now,
            updated_at=now,
        )
        return Response(
            {
                "detail": "All notifications marked as read.",
                "count": updated_count,
            },
            status=status.HTTP_200_OK
        )


class NotificationUnreadCountView(APIView):
    """
    Returns the count of unread notifications for the notification bell badge.
    GET /api/home/notifications/unread-count/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).count()
        return Response(
            {"unread_count": unread_count},
            status=status.HTTP_200_OK
        )

