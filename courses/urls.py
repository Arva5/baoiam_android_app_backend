from django.urls import path

from .views import (
    CategoryListView,
    CourseDetailView,
    CourseListView,
    PromotionalBannerListView,
    TipOfTheDayView,
    UserEnrollmentListView,
    WhyChooseUsListView,
)

urlpatterns = [
    path('', CourseListView.as_view(), name='course-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('promotions/', PromotionalBannerListView.as_view(), name='promotions-list'),
    path('tip-of-the-day/', TipOfTheDayView.as_view(), name='tip-of-the-day'),
    path('why-choose-us/', WhyChooseUsListView.as_view(), name='why-choose-us-list'),
    path('my-enrollments/', UserEnrollmentListView.as_view(), name='user-enrollments'),
    path('<int:id>/', CourseDetailView.as_view(), name='course-detail'),
    path('<slug:slug>/', CourseDetailView.as_view(), name='course-detail-slug'),
    path('courses/', CourseListView.as_view(), name='course-list-alt'),
    path('courses/<slug:slug>/', CourseDetailView.as_view(), name='course-detail-alt'),
]
