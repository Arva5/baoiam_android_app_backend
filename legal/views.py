from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView



from .models import LegalDocument, UserAgreement
from .serializers import (
    AcceptAgreementSerializer,
    LegalDocumentSerializer,
    UserAgreementSerializer,
)


class LegalDocumentView(APIView):
    """
    GET /api/legal/terms/    -> current active Terms & Conditions
    GET /api/legal/privacy/  -> current active Privacy Policy

    Public, no auth needed - the signup screen calls this before the user
    even has an account. Content is whatever is active in Django admin, so
    changing wording/version there reflects immediately with no app update.
    """

    permission_classes = [AllowAny]

    def get(self, request, doc_type):
        document = LegalDocument.objects.filter(
            doc_type=doc_type, is_active=True
        ).first()
        if document is None:
            return Response(
                {"success": False, "errors": [f"No active '{doc_type}' document is configured."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"success": True, "data": LegalDocumentSerializer(document).data})


class AcceptLegalDocumentView(APIView):
    """
    POST /api/legal/accept/   { "doc_type": "terms" }
    Records that the logged-in user accepted the CURRENT active version of
    that document. Call this right after/alongside signup, once the user
    has ticked the "I agree to Terms & Privacy Policy" checkbox.
    """


    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AcceptAgreementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doc_type = serializer.validated_data["doc_type"]

        document = get_object_or_404(LegalDocument, doc_type=doc_type, is_active=True)
        agreement = UserAgreement.objects.create(
            user_email=request.user.email, document=document
        )
        return Response(
            {"success": True, "data": UserAgreementSerializer(agreement).data},
            status=status.HTTP_201_CREATED,
        )
