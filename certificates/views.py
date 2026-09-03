from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Certificate, UserCertificate
from .serializers import CertificateSerializer, UserCertificateSerializer


class CertificateListView(generics.ListAPIView):
    queryset = Certificate.objects.filter(is_active=True).select_related('course')
    serializer_class = CertificateSerializer
    permission_classes = [AllowAny]


class CertificateDetailView(generics.RetrieveAPIView):
    queryset = Certificate.objects.filter(is_active=True).select_related('course')
    serializer_class = CertificateSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'


class UserCertificateListView(generics.ListAPIView):
    serializer_class = UserCertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserCertificate.objects.filter(user=self.request.user).select_related('certificate', 'certificate__course', 'user')


class VerifyCertificateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, certificate_code):
        user_cert = get_object_or_404(
            UserCertificate.objects.select_related('certificate', 'certificate__course', 'user'),
            certificate_code=certificate_code,
            is_verified=True
        )
        return Response({
            'is_valid': True,
            'certificate': UserCertificateSerializer(user_cert).data
        }, status=status.HTTP_200_OK)

