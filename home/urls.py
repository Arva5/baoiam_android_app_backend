from django.urls import path
from .views import (
    GettingStartedView,
    HomeScreenEngagementView,
    LearningPathQuizView,
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
    NotificationUnreadCountView,
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

    # Notifications API for Home Screen Bell
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/unread-count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
    path('notifications/read-all/', NotificationMarkAllReadView.as_view(), name='notification-read-all'),
    path('notifications/mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('notifications/<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('notifications/<int:pk>/', NotificationMarkReadView.as_view(), name='notification-detail'),
]
