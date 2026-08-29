from rest_framework import serializers

from .models import LegalDocument, UserAgreement


class LegalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalDocument
        fields = ["doc_type", "version", "title", "content", "updated_at"]
        read_only_fields = fields


class AcceptAgreementSerializer(serializers.Serializer):
    doc_type = serializers.ChoiceField(choices=LegalDocument.DOC_TYPE_CHOICES)


class UserAgreementSerializer(serializers.ModelSerializer):
    document = LegalDocumentSerializer(read_only=True)

    class Meta:
        model = UserAgreement
        fields = ["document", "accepted_at"]
        read_only_fields = fields
