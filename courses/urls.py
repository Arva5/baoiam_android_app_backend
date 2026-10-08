from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .admin_api import (
    AdminContentItemViewSet,
    AdminCourseViewSet,
    AdminEnrollmentViewSet,
    AdminLessonViewSet,
    AdminModuleViewSet,
    AdminStatsView,
)
from .views import (
    CategoryListView,
    ContentPlayView,
    CourseDetailView,
    CourseEnrollView,
    CourseListView,
    CourseSaveView,
    LessonCompleteView,
    LessonPlayView,
    PromotionalBannerListView,
    SavedCoursesListView,
    TipOfTheDayView,
    UserEnrollmentListView,
    WhyChooseUsListView,
)

# Staff-only management APIs: /api/courses/manage/...
manage_router = SimpleRouter()
manage_router.register('courses', AdminCourseViewSet, basename='manage-course')
manage_router.register('modules', AdminModuleViewSet, basename='manage-module')
manage_router.register('lessons', AdminLessonViewSet, basename='manage-lesson')
manage_router.register('content-items', AdminContentItemViewSet, basename='manage-content-item')
manage_router.register('enrollments', AdminEnrollmentViewSet, basename='manage-enrollment')

urlpatterns = [
    path('manage/stats/', AdminStatsView.as_view(), name='manage-stats'),
    path('manage/', include(manage_router.urls)),
    path('', CourseListView.as_view(), name='course-list'),
    path('saved/', SavedCoursesListView.as_view(), name='saved-courses-list'),
    path('content/<int:id>/play/', ContentPlayView.as_view(), name='content-play'),
    path('lessons/<int:id>/play/', LessonPlayView.as_view(), name='lesson-play'),
    path('lessons/<int:id>/complete/', LessonCompleteView.as_view(), name='lesson-complete'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('promotions/', PromotionalBannerListView.as_view(), name='promotions-list'),
    path('tip-of-the-day/', TipOfTheDayView.as_view(), name='tip-of-the-day'),
    path('why-choose-us/', WhyChooseUsListView.as_view(), name='why-choose-us-list'),
    path('my-enrollments/', UserEnrollmentListView.as_view(), name='user-enrollments'),
    path('<int:id>/enroll/', CourseEnrollView.as_view(), name='course-enroll'),
    path('<slug:slug>/enroll/', CourseEnrollView.as_view(), name='course-enroll-slug'),
    path('<int:id>/save/', CourseSaveView.as_view(), name='course-save-id'),
    path('<slug:slug>/save/', CourseSaveView.as_view(), name='course-save-slug'),
    path('<int:id>/', CourseDetailView.as_view(), name='course-detail'),
    path('<slug:slug>/', CourseDetailView.as_view(), name='course-detail-slug'),
    path('courses/', CourseListView.as_view(), name='course-list-alt'),
    path('courses/<slug:slug>/', CourseDetailView.as_view(), name='course-detail-alt'),
]