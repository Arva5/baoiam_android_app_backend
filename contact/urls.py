# ============================================================
# YEH POORI FILE hai contact/urls.py ke liye —
# apni PURANI urls.py ko isse PURA REPLACE kar do
# ============================================================

from django.urls import path
from .views import (
    ContactMessageCreateView,
    ContactScreenView,
    PopularQuestionDetailView,
    PopularQuestionListView,
    ContactMessageListView,       # <-- NAYA
    MyContactMessagesView,        # <-- NAYA
    ContactMessageDetailView,     # <-- NAYA (yeh GET + PATCH dono handle karta hai)
)

urlpatterns = [
    path('', ContactScreenView.as_view(), name='contact-screen'),
    path('info/', ContactScreenView.as_view(), name='contact-screen-info'),
    path('message/', ContactMessageCreateView.as_view(), name='contact-message-create'),
    path('questions/', PopularQuestionListView.as_view(), name='popular-questions-list'),
    path('questions/<int:pk>/', PopularQuestionDetailView.as_view(), name='popular-question-detail'),

    # ---------- NAYE 4 ENDPOINTS ----------
    # IMPORTANT: messages/my/ ko messages/<int:pk>/ se PEHLE rakhna zaroori hai,
    # warna Django 'my' ko ek pk (id) samajhne ki koshish karega aur error dega.
    path('messages/', ContactMessageListView.as_view(), name='contact-messages-list'),
    path('messages/my/', MyContactMessagesView.as_view(), name='contact-messages-my'),
    path('messages/<int:pk>/', ContactMessageDetailView.as_view(), name='contact-message-detail'),
    # ^ ek hi path GET (detail) aur PATCH (update) dono handle karta hai — see views.py
]