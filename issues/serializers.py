from rest_framework import serializers
from .models import IssueReport


class IssueReportCreateSerializer(serializers.ModelSerializer):
    description = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={
            'blank': 'This field may not be blank.',
            'required': 'This field is required.',
        },
    )

    class Meta:
        model = IssueReport
        fields = ['id', 'description', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']


class IssueReportListSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = IssueReport
        fields = ['id', 'user_email', 'description', 'status', 'created_at']

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None


class IssueReportStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=IssueReport.STATUS_CHOICES, required=False)
    admin_notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = IssueReport
        fields = ['status', 'admin_notes']
