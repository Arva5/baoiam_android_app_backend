from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    GettingStartedSerializer,
    HomeScreenEngagementSerializer,
    LearningPathQuizHomeSerializer,
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
