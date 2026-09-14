from django.urls import path
from .views import (
    IssueReportCreateView,
    IssueReportDetailView,
    IssueReportListView,
)

urlpatterns = [
    # 1. Android Client Submit API
    path('report/', IssueReportCreateView.as_view(), name='issue-report-create'),

    # 2. Admin List & Detail/Status Update APIs
    path('', IssueReportListView.as_view(), name='issues-list'),
    path('<int:pk>/', IssueReportDetailView.as_view(), name='issue-detail'),
]
