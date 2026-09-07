"""
Notification URL patterns mounted at /api/notifications/.

These views are implemented in home.views and use the home.Notification model.
This file provides the dedicated /api/notifications/ prefix requested by the
HS1 Home Screen spec without requiring a separate Django app.
"""
from django.urls import path

from .views import (
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
    NotificationUnreadCountView,
)

urlpatterns = [
    # GET  /api/notifications/              — list user's notifications (?unread=true)
    path("", NotificationListView.as_view(), name="notification-list"),

    # GET  /api/notifications/unread-count/ — bell badge count
    path("unread-count/", NotificationUnreadCountView.as_view(), name="notification-unread-count"),

    # POST /api/notifications/mark-all-read/ — mark all as read
    path("mark-all-read/", NotificationMarkAllReadView.as_view(), name="notification-mark-all-read"),

    # PATCH /api/notifications/<pk>/read/   — mark single notification as read
    path("<int:pk>/read/", NotificationMarkReadView.as_view(), name="notification-mark-read"),
]
