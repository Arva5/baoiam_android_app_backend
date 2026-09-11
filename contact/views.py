import logging
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from .models import ContactMessage, ContactSupportChannel, PopularQuestion
from .serializers import (
    DEFAULT_SUBJECT_OPTIONS,
    ContactMessageCreateSerializer,
    ContactMessageDetailSerializer,
    ContactMessageListSerializer,
    ContactMessageStatusUpdateSerializer,
    ContactScreenDataSerializer,
    ContactSupportChannelSerializer,
    PopularQuestionSerializer,
    ContactMessageDetailSerializer,        # yeh naya add karo
    ContactMessageStatusUpdateSerializer,
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


class ContactMessageListView(APIView):
    """
    GET /api/contact/messages/
    List all submitted contact inquiries with optional filtering:
    - ?status=pending|in_progress|resolved|closed
    - ?email=example@domain.com
    - ?search=keyword

    POST /api/contact/messages/
    Submit a new contact message (same payload as /message/).
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = ContactMessage.objects.all().order_by('-created_at')

        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter.strip())

        # Filter by email
        email_filter = request.query_params.get('email')
        if email_filter:
            queryset = queryset.filter(email__iexact=email_filter.strip())

        # General search keyword
        search_query = request.query_params.get('search')
        if search_query:
            q = search_query.strip()
            queryset = queryset.filter(
                Q(name__icontains=q)
                | Q(email__icontains=q)
                | Q(subject__icontains=q)
                | Q(message__icontains=q)
            )

        serializer = ContactMessageListSerializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "count": queryset.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        return ContactMessageCreateView().post(request)


class UserMyContactMessagesView(APIView):
    """
    GET /api/contact/messages/my/
    Returns inquiries sent by the current authenticated user (or by ?email= for guests).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            queryset = ContactMessage.objects.filter(
                Q(user=request.user) | Q(email__iexact=request.user.email)
            ).order_by('-created_at')
        else:
            email = request.query_params.get('email')
            if not email:
                return Response(
                    {
                        "success": False,
                        "errors": ["Please log in or provide '?email=' parameter to view your messages."],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = ContactMessage.objects.filter(email__iexact=email.strip()).order_by('-created_at')

        serializer = ContactMessageListSerializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "count": queryset.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ContactMessageDetailView(APIView):
    """
    GET /api/contact/messages/<int:pk>/
    Retrieve single inquiry details.

    PATCH /api/contact/messages/<int:pk>/
    Update inquiry status ('pending', 'in_progress', 'resolved', 'closed') or admin_notes.

    DELETE /api/contact/messages/<int:pk>/
    Delete inquiry record.
    """
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ContactMessage.objects.get(pk=pk)
        except ContactMessage.DoesNotExist:
            return None

    def get(self, request, pk):
        message = self.get_object(pk)
        if not message:
            return Response(
                {"success": False, "errors": [f"Contact message with ID {pk} not found."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ContactMessageDetailSerializer(message)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        message = self.get_object(pk)
        if not message:
            return Response(
                {"success": False, "errors": [f"Contact message with ID {pk} not found."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ContactMessageStatusUpdateSerializer(message, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        updated_message = serializer.save()
        return Response(
            {
                "success": True,
                "message": "Contact message updated successfully.",
                "data": ContactMessageDetailSerializer(updated_message).data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        message = self.get_object(pk)
        if not message:
            return Response(
                {"success": False, "errors": [f"Contact message with ID {pk} not found."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        message.delete()
        return Response(
            {"success": True, "message": f"Contact message {pk} deleted successfully."},
            status=status.HTTP_200_OK,
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
# ============================================================
# STEP A: Yeh IMPORTS file ke TOP mein already maujood imports
# ke saath UPDATE/ADD karo
# ============================================================

# Purana import tha:
#   from rest_framework.permissions import AllowAny
# Ise is line se REPLACE karo:
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

# Aur serializers import mein yeh 2 naye add karo:
from .serializers import (
    DEFAULT_SUBJECT_OPTIONS,
    ContactMessageCreateSerializer,
    ContactScreenDataSerializer,
    ContactSupportChannelSerializer,
    PopularQuestionSerializer,
    ContactMessageDetailSerializer,        # <-- NAYA
    ContactMessageStatusUpdateSerializer,  # <-- NAYA
)


# ============================================================
# STEP B: Yeh 4 NAYI CLASSES file ke END MEIN ADD KARO
# (existing classes ko chhedo mat)
# ============================================================

class ContactMessageListView(generics.ListAPIView):
    """
    GET /api/contact/messages/
    Saare contact messages ki list — SIRF ADMIN/STAFF ke liye.
    Optional filters: ?status=pending  ya  ?email=someone@gmail.com
    """
    permission_classes = [IsAdminUser]   # <-- sirf admin/staff allowed
    serializer_class = ContactMessageDetailSerializer

    def get_queryset(self):
        queryset = ContactMessage.objects.all().order_by('-created_at')
        status_filter = self.request.query_params.get('status')
        email_filter = self.request.query_params.get('email')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if email_filter:
            queryset = queryset.filter(email__iexact=email_filter)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "count": queryset.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class MyContactMessagesView(generics.ListAPIView):
    """
    GET /api/contact/messages/my/
    Sirf LOGGED-IN user ke apne bheje messages — normal user bhi use kar sakta hai.
    """
    permission_classes = [IsAuthenticated]   # <-- login zaroori, admin hona zaroori nahi
    serializer_class = ContactMessageDetailSerializer

    def get_queryset(self):
        return ContactMessage.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "count": queryset.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ContactMessageDetailView(APIView):
    """
    SAME URL handles BOTH:
      GET   /api/contact/messages/<id>/   -> poori detail dikhao
      PATCH /api/contact/messages/<id>/   -> sirf status/admin_notes update karo
    SIRF ADMIN/STAFF ke liye (dono methods).

    NOTE: GET aur PATCH ko EK hi class mein rakhna zaroori hai, kyunki Django
    URL routing method (GET/PATCH) ke hisaab se alag view select nahi karta —
    same path pe do alag classes register karoge toh conflict/wrong-behavior hoga.
    """
    permission_classes = [IsAdminUser]   # <-- sirf admin/staff allowed (GET aur PATCH dono)

    def get_object(self, pk):
        try:
            return ContactMessage.objects.get(pk=pk)
        except ContactMessage.DoesNotExist:
            return None

    def get(self, request, pk):
        instance = self.get_object(pk)
        if instance is None:
            return Response(
                {"success": False, "errors": ["Contact message not found."]},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ContactMessageDetailSerializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        instance = self.get_object(pk)
        if instance is None:
            return Response(
                {"success": False, "errors": ["Contact message not found."]},
                status=status.HTTP_404_NOT_FOUND,
            )

        # partial=True => sirf jo fields request.data mein bheji hain WOHI update hongi,
        # baaki (name/email/subject/message) UNTOUCHED rahengi. Isse purana bug fix ho jata hai.
        serializer = ContactMessageStatusUpdateSerializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()

        # Response mein FULL detail bhejo (sirf status/admin_notes nahi)
        full_serializer = ContactMessageDetailSerializer(instance)
        return Response(
            {
                "success": True,
                "message": "Contact message updated successfully.",
                "data": full_serializer.data,
            },
            status=status.HTTP_200_OK,
        )