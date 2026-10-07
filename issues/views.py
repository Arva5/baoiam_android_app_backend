from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import IssueReport
from .serializers import (
    IssueReportCreateSerializer,
    IssueReportListSerializer,
    IssueReportStatusUpdateSerializer,
)


class IssueReportCreateView(APIView):
    """
    POST /api/issues/report/
    Submit a bug or issue report from the Android app.
    Requires user authentication token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = IssueReportCreateSerializer(data=request.data)
        if not serializer.is_valid():
            # Format errors list to match spec e.g. ["This field may not be blank."]
            error_list = []
            for field, messages in serializer.errors.items():
                if isinstance(messages, list):
                    error_list.extend([str(m) for m in messages])
                else:
                    error_list.append(str(messages))

            return Response(
                {
                    "success": False,
                    "errors": error_list,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        report = serializer.save(user=request.user)
        return Response(
            {
                "success": True,
                "data": IssueReportCreateSerializer(report).data,
            },
            status=status.HTTP_201_CREATED,
        )


class IssueReportListView(APIView):
    """
    GET /api/issues/
    List all reported issues with optional filtering:
    - ?status=open|in_progress|resolved
    - ?user_email=email@domain.com
    Staff/Admin access only.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = IssueReport.objects.all().order_by('-created_at')

        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter.strip())

        # Filter by user email
        user_email = request.query_params.get('user_email')
        if user_email:
            queryset = queryset.filter(user__email__iexact=user_email.strip())

        serializer = IssueReportListSerializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class IssueReportDetailView(APIView):
    """
    GET /api/issues/<int:pk>/
    Retrieve single issue report details.

    PATCH /api/issues/<int:pk>/
    Update status ('open', 'in_progress', 'resolved') or admin_notes.

    DELETE /api/issues/<int:pk>/
    Delete issue report.
    Staff/Admin access only.
    """
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return IssueReport.objects.get(pk=pk)
        except IssueReport.DoesNotExist:
            return None

    def get(self, request, pk):
        report = self.get_object(pk)
        if not report:
            return Response(
                {"success": False, "errors": [f"Issue report with ID {pk} not found."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = IssueReportListSerializer(report)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        report = self.get_object(pk)
        if not report:
            return Response(
                {"success": False, "errors": [f"Issue report with ID {pk} not found."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = IssueReportStatusUpdateSerializer(report, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        updated_report = serializer.save()
        return Response(
            {
                "success": True,
                "message": "Issue report updated successfully.",
                "data": IssueReportListSerializer(updated_report).data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        report = self.get_object(pk)
        if not report:
            return Response(
                {"success": False, "errors": [f"Issue report with ID {pk} not found."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        report.delete()
        return Response(
            {"success": True, "message": f"Issue report {pk} deleted successfully."},
            status=status.HTTP_200_OK,
        )
