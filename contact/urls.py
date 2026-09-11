from django.urls import path
from .views import (
    ContactMessageCreateView,
    ContactMessageDetailView,
    ContactMessageListView,
    ContactScreenView,
    PopularQuestionDetailView,
    PopularQuestionListView,
    UserMyContactMessagesView,
)

urlpatterns = [
    path('', ContactScreenView.as_view(), name='contact-screen'),
    path('info/', ContactScreenView.as_view(), name='contact-screen-info'),
    path('message/', ContactMessageCreateView.as_view(), name='contact-message-create'),
    path('messages/', ContactMessageListView.as_view(), name='contact-messages-list'),
    path('messages/my/', UserMyContactMessagesView.as_view(), name='contact-messages-my'),
    path('messages/<int:pk>/', ContactMessageDetailView.as_view(), name='contact-messages-detail'),
    path('questions/', PopularQuestionListView.as_view(), name='popular-questions-list'),
    path('questions/<int:pk>/', PopularQuestionDetailView.as_view(), name='popular-question-detail'),
]
