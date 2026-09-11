from rest_framework import serializers
from .models import ContactMessage, ContactSupportChannel, PopularQuestion

DEFAULT_SUBJECT_OPTIONS = [
    "General Inquiry",
    "Course & Content Inquiry",
    "Payment & Billing",
    "Technical Issues",
    "Account & Password",
    "Cancel Subscription",
    "Feedback / Suggestions",
    "Other",
]


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=150, trim_whitespace=True)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=200, trim_whitespace=True)
    message = serializers.CharField(trim_whitespace=True)

    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required.")
        return value.strip()

    def validate_subject(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Subject is required.")
        return value.strip()

    def validate_message(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Message is required.")
        return value.strip()


class ContactMessageListSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True, default=None)

    class Meta:
        model = ContactMessage
        fields = [
            'id',
            'name',
            'email',
            'subject',
            'message',
            'status',
            'admin_notes',
            'user',
            'user_email',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class ContactMessageDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True, default=None)

    class Meta:
        model = ContactMessage
        fields = [
            'id',
            'name',
            'email',
            'subject',
            'message',
            'status',
            'admin_notes',
            'user',
            'user_email',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'name',
            'email',
            'subject',
            'message',
            'user',
            'user_email',
            'created_at',
            'updated_at',
        ]


class ContactMessageStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=False)
    admin_notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = ContactMessage
        fields = ['status', 'admin_notes']

    def validate_status(self, value):
        valid_statuses = dict(ContactMessage.STATUS_CHOICES).keys()
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status '{value}'. Choose from: {', '.join(valid_statuses)}"
            )
        return value


class ContactSupportChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSupportChannel
        fields = ['id', 'channel_type', 'title', 'subtitle', 'value']


class PopularQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopularQuestion
        fields = ['id', 'question', 'answer', 'category']


class SupportBadgeSerializer(serializers.Serializer):
    title = serializers.CharField(default="24/7 Support Available")
    subtitle = serializers.CharField(default="Average response time: 2 minutes")


class ContactScreenDataSerializer(serializers.Serializer):
    title = serializers.CharField(default="Contact Us")
    heading = serializers.CharField(default="How can we help?")
    subtitle = serializers.CharField(
        default="We're here to assist you 24/7. Choose your preferred way to reach us."
    )
    channels = ContactSupportChannelSerializer(many=True)
    subject_options = serializers.ListField(
        child=serializers.CharField()
    )
    popular_questions = PopularQuestionSerializer(many=True)
    support_badge = SupportBadgeSerializer()


