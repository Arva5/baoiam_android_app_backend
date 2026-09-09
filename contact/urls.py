from django.urls import path
from .views import (
    ContactMessageCreateView,
    ContactScreenView,
    PopularQuestionDetailView,
    PopularQuestionListView,
)

urlpatterns = [
    path('', ContactScreenView.as_view(), name='contact-screen'),
    path('info/', ContactScreenView.as_view(), name='contact-screen-info'),
    path('message/', ContactMessageCreateView.as_view(), name='contact-message-create'),
    path('questions/', PopularQuestionListView.as_view(), name='popular-questions-list'),
    path('questions/<int:pk>/', PopularQuestionDetailView.as_view(), name='popular-question-detail'),
]
