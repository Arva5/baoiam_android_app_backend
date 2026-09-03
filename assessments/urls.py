from django.urls import path
from .views import (
    AssessmentDetailView,
    AssessmentListView,
    FeaturedQuizView,
    SubmitAssessmentView,
    UserAttemptsListView,
)

urlpatterns = [
    path('', AssessmentListView.as_view(), name='assessment-list'),
    path('featured-quiz/', FeaturedQuizView.as_view(), name='featured-quiz'),
    path('<int:id>/', AssessmentDetailView.as_view(), name='assessment-detail'),
    path('<int:id>/submit/', SubmitAssessmentView.as_view(), name='submit-quiz'),
    path('my-attempts/', UserAttemptsListView.as_view(), name='user-attempts'),
]
