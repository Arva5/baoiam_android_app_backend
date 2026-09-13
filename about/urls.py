from django.urls import path
from .views import (
    AboutOverviewView,
    AboutUsScreenView,
    ImpactStatDetailView,
    ImpactStatListCreateView,
    SuccessStoryDetailView,
    SuccessStoryListCreateView,
    SuccessStorySubmitView,
    TeamMemberDetailView,
    TeamMemberListCreateView,
    WhyChooseUsDetailView,
    WhyChooseUsListCreateView,
)

urlpatterns = [
    # 1. Main Android Client Endpoint
    path('', AboutUsScreenView.as_view(), name='about-screen'),
    path('screen/', AboutUsScreenView.as_view(), name='about-screen-alt'),

    # 2. Overview & Mission Management
    path('overview/', AboutOverviewView.as_view(), name='about-overview'),

    # 3. Impact Stats Endpoints
    path('stats/', ImpactStatListCreateView.as_view(), name='about-stats-list-create'),
    path('stats/<int:pk>/', ImpactStatDetailView.as_view(), name='about-stats-detail'),

    # 4. What We Offer / Why Choose Us Endpoints
    path('offers/', WhyChooseUsListCreateView.as_view(), name='about-offers-list-create'),
    path('offers/<int:pk>/', WhyChooseUsDetailView.as_view(), name='about-offers-detail'),
    path('what-we-offer/', WhyChooseUsListCreateView.as_view(), name='about-what-we-offer-list-create'),
    path('what-we-offer/<int:pk>/', WhyChooseUsDetailView.as_view(), name='about-what-we-offer-detail'),

    # 5. Success Stories Endpoints & User Submission
    path('stories/', SuccessStoryListCreateView.as_view(), name='about-stories-list-create'),
    path('stories/<int:pk>/', SuccessStoryDetailView.as_view(), name='about-stories-detail'),
    path('stories/submit/', SuccessStorySubmitView.as_view(), name='about-story-submit'),

    # 6. Team Members Endpoints
    path('team/', TeamMemberListCreateView.as_view(), name='about-team-list-create'),
    path('team/<int:pk>/', TeamMemberDetailView.as_view(), name='about-team-detail'),
]
