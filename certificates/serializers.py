from rest_framework import serializers
from .models import Certificate, UserCertificate


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Certificate
        fields = (
            'id',
            'title',
            'description',
            'course',
            'course_title',
            'badge_icon_url',
            'issuer_name',
            'is_active',
            'created_at',
        )


class UserCertificateSerializer(serializers.ModelSerializer):
    certificate = CertificateSerializer(read_only=True)
    recipient_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = UserCertificate
        fields = (
            'id',
            'recipient_name',
            'certificate',
            'certificate_code',
            'issued_at',
            'certificate_url',
            'is_verified',
        )

