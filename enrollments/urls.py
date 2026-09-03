from django.urls import path

from .views import EnrollmentDetailView, EnrollmentListCreateView

urlpatterns = [
    path("enrollments/", EnrollmentListCreateView.as_view(), name="enrollment-list-create"),
    path("enrollments/<slug:course_slug>/", EnrollmentDetailView.as_view(), name="enrollment-detail"),
]
