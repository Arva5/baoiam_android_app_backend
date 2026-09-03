from django.urls import path
from .views import (
    GettingStartedView,
    HomeScreenEngagementView,
    LearningPathQuizView,
    PromotionalBannersView,
    StartYourJourneyView,
    TipOfTheDayView,
    WhyChooseUsView,
)

urlpatterns = [
    path('', HomeScreenEngagementView.as_view(), name='home-engagement'),
    path('screen1/', HomeScreenEngagementView.as_view(), name='home-screen1'),
    path('engagement/', HomeScreenEngagementView.as_view(), name='home-engagement-alias'),
    path('getting-started/', GettingStartedView.as_view(), name='home-getting-started'),
    path('promotional-banners/', PromotionalBannersView.as_view(), name='home-promotional-banners'),
    path('learning-path-quiz/', LearningPathQuizView.as_view(), name='home-learning-path-quiz'),
    path('why-choose-us/', WhyChooseUsView.as_view(), name='home-why-choose-us'),
    path('tip-of-the-day/', TipOfTheDayView.as_view(), name='home-tip-of-the-day'),
    path('start-your-journey/', StartYourJourneyView.as_view(), name='home-start-your-journey'),
]
