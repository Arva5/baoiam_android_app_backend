from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import FeedbackSerializer


class FeedbackCreateView(APIView):
    """
    POST /api/feedback/
    Submit app feedback. Authentication required.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(
            {
                "message": "Thank you for your feedback!",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
