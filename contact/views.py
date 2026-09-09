import logging
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ContactMessage, ContactSupportChannel, PopularQuestion
from .serializers import (
    DEFAULT_SUBJECT_OPTIONS,
    ContactMessageCreateSerializer,
    ContactScreenDataSerializer,
    ContactSupportChannelSerializer,
    PopularQuestionSerializer,
)

logger = logging.getLogger(__name__)

FALLBACK_CHANNELS = [
    {
        "id": 1,
        "channel_type": "live_chat",
        "title": "Live Chat",
        "subtitle": "2 min response",
        "value": "",
    },
    {
        "id": 2,
        "channel_type": "call",
        "title": "Call Us",
        "subtitle": "24/7 support",
        "value": "+91-9999999999",
    },
    {
        "id": 3,
        "channel_type": "email",
        "title": "Email",
        "subtitle": "4 hr response",
        "value": "support@baoiam.com",
    },
]

FALLBACK_POPULAR_QUESTIONS = [
    {
        "id": 1,
        "question": "How to reset password?",
        "answer": "Go to the Login screen, click on 'Forgot Password', enter your registered email address, and verify the OTP sent to your inbox to reset your password.",
        "category": "Account",
    },
    {
        "id": 2,
        "question": "Cancel subscription",
        "answer": "You can manage or cancel your subscription by visiting your Profile -> Manage Subscriptions or by reaching out to our support team.",
        "category": "Billing",
    },
    {
        "id": 3,
        "question": "Payment methods",
        "answer": "We accept all major credit/debit cards, Net Banking, UPI (Google Pay, PhonePe, Paytm), and popular wallets.",
        "category": "Payment",
    },
    {
        "id": 4,
        "question": "Technical issues",
        "answer": "Please ensure your app is updated to the latest version. If the issue persists, clear app cache or submit a message using the form above with screenshots.",
        "category": "Technical",
    },
]


class ContactScreenView(APIView):
    """
    Returns aggregated data for the Contact Us screen:
    - Support channels (Live Chat, Call Us, Email)
    - Subject options for the form dropdown
    - Popular questions list
    - 24/7 Support badge info
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # Retrieve active channels from DB, or use fallback if empty
        channels_qs = ContactSupportChannel.objects.filter(is_active=True).order_by('display_order', 'id')
        if channels_qs.exists():
            channels_data = ContactSupportChannelSerializer(channels_qs, many=True).data
        else:
            channels_data = FALLBACK_CHANNELS

        # Retrieve active popular questions from DB, or use fallback if empty
        questions_qs = PopularQuestion.objects.filter(is_active=True).order_by('display_order', 'id')
        if questions_qs.exists():
            questions_data = PopularQuestionSerializer(questions_qs, many=True).data
        else:
            questions_data = FALLBACK_POPULAR_QUESTIONS

        screen_payload = {
            "title": "Contact Us",
            "heading": "How can we help?",
            "subtitle": "We're here to assist you 24/7. Choose your preferred way to reach us.",
            "channels": channels_data,
            "subject_options": DEFAULT_SUBJECT_OPTIONS,
            "popular_questions": questions_data,
            "support_badge": {
                "title": "24/7 Support Available",
                "subtitle": "Average response time: 2 minutes",
            },
        }

        serializer = ContactScreenDataSerializer(data=screen_payload)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ContactMessageCreateView(APIView):
    """
    Submit a 'Send us a message' contact form inquiry.
    Allows both guest and authenticated users.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ContactMessageCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Associate authenticated user if available
        user = request.user if request.user.is_authenticated else None
        contact_message = serializer.save(user=user)

        logger.info(
            f"New contact message received from {contact_message.name} <{contact_message.email}> - Subject: {contact_message.subject}"
        )

        return Response(
            {
                "success": True,
                "message": "Your message has been sent successfully. Our support team will reach out to you shortly.",
                "data": ContactMessageCreateSerializer(contact_message).data,
            },
            status=status.HTTP_201_CREATED,
        )


class PopularQuestionListView(generics.ListAPIView):
    """
    List all popular FAQ questions.
    """
    permission_classes = [AllowAny]
    serializer_class = PopularQuestionSerializer

    def get_queryset(self):
        return PopularQuestion.objects.filter(is_active=True).order_by('display_order', 'id')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"success": True, "data": FALLBACK_POPULAR_QUESTIONS},
                status=status.HTTP_200_OK,
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)


class PopularQuestionDetailView(generics.RetrieveAPIView):
    """
    Retrieve single popular question by ID.
    """
    permission_classes = [AllowAny]
    serializer_class = PopularQuestionSerializer
    queryset = PopularQuestion.objects.filter(is_active=True)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception:
            # Check if pk matches fallback
            pk = kwargs.get('pk')
            match = next((q for q in FALLBACK_POPULAR_QUESTIONS if q['id'] == pk), None)
            if match:
                return Response({"success": True, "data": match}, status=status.HTTP_200_OK)
            return Response(
                {"success": False, "errors": ["Popular question not found."]},
                status=status.HTTP_404_NOT_FOUND,
            )
