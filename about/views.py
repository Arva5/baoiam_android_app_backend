from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AboutOverview, ImpactStat, WhyChooseUsItem, SuccessStory, TeamMember
from .serializers import (
    AboutOverviewSerializer,
    AboutUsScreenDataSerializer,
    ImpactStatSerializer,
    SuccessStorySerializer,
    SuccessStorySubmitSerializer,
    TeamMemberSerializer,
    WhyChooseUsItemSerializer,
)

# Default Fallback Data matching Kotlin AboutUsUiState exactly
FALLBACK_MISSION_TEXT = (
    "To democratize education by providing accessible, high-quality learning "
    "experiences that empower learners worldwide to achieve their full potential."
)

FALLBACK_IMPACT_STATS = [
    {"id": "1", "value": "1M+", "label": "Students", "icon": "Groups"},
    {"id": "2", "value": "5000+", "label": "Courses", "icon": "MenuBook"},
    {"id": "3", "value": "98%", "label": "Success Rate", "icon": "Star"},
    {"id": "4", "value": "150+", "label": "Countries", "icon": "Public"},
]

FALLBACK_WHAT_WE_OFFER = [
    {"id": "1", "title": "Expert Instructors", "description": "Learn from industry professionals", "icon": "School"},
    {"id": "2", "title": "Live Classes", "description": "Interactive learning experience", "icon": "VideoCall"},
    {"id": "3", "title": "24/7 Support", "description": "Always here to help you", "icon": "SupportAgent"},
    {"id": "4", "title": "Mobile Learning", "description": "Learn on the go, anywhere", "icon": "PhoneAndroid"},
    {"id": "5", "title": "Certification", "description": "Industry-recognized credentials", "icon": "WorkspacePremium"},
    {"id": "6", "title": "Personal Growth", "description": "Achieve your career goals", "icon": "TrendingUp"},
]

FALLBACK_SUCCESS_STORIES = [
    {
        "id": "1",
        "name": "Peter Jones",
        "role": "UNIV Business School",
        "rating": 5,
        "story": "The interactive learning app took my skills to the next level. I landed my dream job right after completing the program.",
    },
    {
        "id": "2",
        "name": "Mia Morris",
        "role": "Web Developer",
        "rating": 5,
        "story": "The practical projects and mentor support were invaluable in helping me transition into web development.",
    },
]

FALLBACK_TEAM_MEMBERS = [
    {"id": "1", "name": "James Perkins", "role": "CEO & Founder"},
    {"id": "2", "name": "Emma Wilson", "role": "Head of Education"},
]

FALLBACK_TRUSTED_BY = ["TechCorp", "EduPlus", "SkillHub", "LearnCo"]


# =====================================================================
# 1. ANDROID CLIENT MAIN API
# =====================================================================

class AboutUsScreenView(APIView):
    """
    GET /api/about-us/
    Aggregated screen endpoint for Android App.
    Returns 1-to-1 payload matching Kotlin data class AboutUsUiState.
    Publicly accessible (AllowAny).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # 1. Mission Text & Trusted Brands
        overview = AboutOverview.objects.filter(is_active=True).first()
        if overview:
            mission_text = overview.mission_text
            trusted_by = overview.trusted_by_labels if overview.trusted_by_labels else FALLBACK_TRUSTED_BY
        else:
            mission_text = FALLBACK_MISSION_TEXT
            trusted_by = FALLBACK_TRUSTED_BY

        # 2. Impact Stats
        stats_qs = ImpactStat.objects.filter(is_active=True).order_by('display_order', 'id')
        if stats_qs.exists():
            impact_stats = [
                {"id": str(s.id), "value": s.value, "label": s.label, "icon": s.icon}
                for s in stats_qs
            ]
        else:
            impact_stats = FALLBACK_IMPACT_STATS

        # 3. What We Offer / Why Choose Us
        offers_qs = WhyChooseUsItem.objects.filter(is_active=True).order_by('display_order', 'id')
        if offers_qs.exists():
            what_we_offer = [
                {"id": str(o.id), "title": o.title, "description": o.description, "icon": o.icon}
                for o in offers_qs
            ]
        else:
            what_we_offer = FALLBACK_WHAT_WE_OFFER

        # 4. Success Stories
        stories_qs = SuccessStory.objects.filter(is_active=True).order_by('display_order', 'id')
        if stories_qs.exists():
            success_stories = [
                {"id": str(st.id), "name": st.name, "role": st.role, "rating": st.rating, "story": st.story}
                for st in stories_qs
            ]
        else:
            success_stories = FALLBACK_SUCCESS_STORIES

        # 5. Team Members
        team_qs = TeamMember.objects.filter(is_active=True).order_by('display_order', 'id')
        if team_qs.exists():
            team_members = [
                {"id": str(t.id), "name": t.name, "role": t.role}
                for t in team_qs
            ]
        else:
            team_members = FALLBACK_TEAM_MEMBERS

        payload = {
            # camelCase matching Kotlin AboutUsUiState
            "missionText": mission_text,
            "impactStats": impact_stats,
            "whatWeOffer": what_we_offer,
            "successStories": success_stories,
            "teamMembers": team_members,
            "trustedByLabels": trusted_by,
            # snake_case alternatives for convenience
            "mission_text": mission_text,
            "impact_stats": impact_stats,
            "what_we_offer": what_we_offer,
            "success_stories": success_stories,
            "team_members": team_members,
            "trusted_by_labels": trusted_by,
        }

        return Response(
            {
                "success": True,
                "data": payload,
            },
            status=status.HTTP_200_OK,
        )


# =====================================================================
# 2. OVERVIEW & MISSION MANAGEMENT
# =====================================================================

class AboutOverviewView(APIView):
    """
    GET /api/about-us/overview/
    Retrieve current overview info (title, mission_text, trusted_by_labels, etc).

    PUT / PATCH /api/about-us/overview/
    Update overview info. (Admin only)
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        obj = AboutOverview.get_solo()
        serializer = AboutOverviewSerializer(obj)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request):
        obj = AboutOverview.get_solo()
        serializer = AboutOverviewSerializer(obj, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        updated_obj = serializer.save()
        return Response(
            {
                "success": True,
                "message": "Overview updated successfully.",
                "data": AboutOverviewSerializer(updated_obj).data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        return self.put(request)


# =====================================================================
# 3. IMPACT STATS CRUD
# =====================================================================

class ImpactStatListCreateView(APIView):
    """
    GET /api/about-us/stats/
    List impact stats.

    POST /api/about-us/stats/
    Create new impact stat. (Admin only)
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        is_admin = request.user and request.user.is_staff
        if is_admin and request.query_params.get('all') == 'true':
            queryset = ImpactStat.objects.all().order_by('display_order', 'id')
        else:
            queryset = ImpactStat.objects.filter(is_active=True).order_by('display_order', 'id')
        serializer = ImpactStatSerializer(queryset, many=True)
        return Response(
            {"success": True, "count": queryset.count(), "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ImpactStatSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(
            {"success": True, "message": "Impact stat created successfully.", "data": ImpactStatSerializer(instance).data},
            status=status.HTTP_201_CREATED,
        )


class ImpactStatDetailView(APIView):
    """
    GET /api/about-us/stats/<id>/
    Retrieve single stat.

    PUT/PATCH /api/about-us/stats/<id>/
    Update stat. (Admin only)

    DELETE /api/about-us/stats/<id>/
    Delete stat. (Admin only)
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_object(self, pk):
        try:
            return ImpactStat.objects.get(pk=pk)
        except ImpactStat.DoesNotExist:
            return None

    def get(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return Response({"success": False, "errors": [f"Impact stat {pk} not found."]}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "data": ImpactStatSerializer(instance).data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return Response({"success": False, "errors": [f"Impact stat {pk} not found."]}, status=status.HTTP_404_NOT_FOUND)
        serializer = ImpactStatSerializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        updated = serializer.save()
        return Response(
            {"success": True, "message": "Impact stat updated successfully.", "data": ImpactStatSerializer(updated).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        return self.patch(request, pk)

    def delete(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return Response({"success": False, "errors": [f"Impact stat {pk} not found."]}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response({"success": True, "message": f"Impact stat {pk} deleted successfully."}, status=status.HTTP_200_OK)


# =====================================================================
# 4. WHAT WE OFFER / WHY CHOOSE US CRUD
# =====================================================================

class WhyChooseUsListCreateView(APIView):
    """
    GET /api/about-us/offers/
    List offers/features.

    POST /api/about-us/offers/
    Create new offer. (Admin only)
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        is_admin = request.user and request.user.is_staff
        if is_admin and request.query_params.get('all') == 'true':
            queryset = WhyChooseUsItem.objects.all().order_by('display_order', 'id')
        else:
            queryset = WhyChooseUsItem.objects.filter(is_active=True).order_by('display_order', 'id')
        serializer = WhyChooseUsItemSerializer(queryset, many=True)
        return Response(
            {"success": True, "count": queryset.count(), "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = WhyChooseUsItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(
            {"success": True, "message": "Offer created successfully.", "data": WhyChooseUsItemSerializer(instance).data},
            status=status.HTTP_201_CREATED,
        )


class WhyChooseUsDetailView(APIView):
    """
    GET /api/about-us/offers/<id>/
    Retrieve single offer.

    PUT/PATCH /api/about-us/offers/<id>/
    Update offer. (Admin only)

    DELETE /api/about-us/offers/<id>/
    Delete offer. (Admin only)
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_object(self, pk):
        try:
            return WhyChooseUsItem.objects.get(pk=pk)
        except WhyChooseUsItem.DoesNotExist:
            return None

    def get(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return Response({"success": False, "errors": [f"Offer {pk} not found."]}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "data": WhyChooseUsItemSerializer(instance).data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return Response({"success": False, "errors": [f"Offer {pk} not found."]}, status=status.HTTP_404_NOT_FOUND)
        serializer = WhyChooseUsItemSerializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        updated = serializer.save()
        return Response(
            {"success": True, "message": "Offer updated successfully.", "data": WhyChooseUsItemSerializer(updated).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        return self.patch(request, pk)

    def delete(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return Response({"success": False, "errors": [f"Offer {pk} not found."]}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response({"success": True, "message": f"Offer {pk} deleted successfully."}, status=status.HTTP_200_OK)


# =====================================================================
# 5. SUCCESS STORIES CRUD & USER SUBMISSION
# =====================================================================

class SuccessStoryListCreateView(APIView):
    """
    GET /api/about-us/stories/
    List success stories.

    POST /api/about-us/stories/
    Create new success story. (Admin only)
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        is_admin = request.user and request.user.is_staff
        if is_admin and request.query_params.get('all') == 'true':
            queryset = SuccessStory.objects.all().order_by('display_order', 'id')
        else:
            queryset = SuccessStory.objects.filter(is_active=True).order_by('display_order', 'id')
        serializer = SuccessStorySerializer(queryset, many=True)
        return Response(
            {"success": True, "count": queryset.count(), "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = SuccessStorySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(
            {"success": True, "message": "Success story created successfully.", "data": SuccessStorySerializer(instance).data},
            status=status.HTTP_201_CREATED,
        )


class SuccessStorySubmitView(APIView):
    """
    POST /api/about-us/stories/submit/
    Public endpoint for Android app users / students to submit testimonials.
    Saves with is_active=False until approved by admin.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SuccessStorySubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(
            {
                "success": True,
                "message": "Thank you for sharing your story! It will be reviewed by our team before appearing publicly.",
                "data": SuccessStorySerializer(instance).data,
            },
            status=status.HTTP_201_CREATED,
        )


class SuccessStoryDetailView(APIView):
    """
    GET /api/about-us/stories/<id>/
    Retrieve single story.

    PUT/PATCH /api/about-us/stories/<id>/
    Update story (e.g. approve is_active=True). (Admin only)

    DELETE /api/about-us/stories/<id>/
    Delete story. (Admin only)
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_object(self, pk):
        try:
            return SuccessStory.objects.get(pk=pk)
        except SuccessStory.DoesNotExist:
            return None

    def get(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return Response({"success": False, "errors": [f"Success story {pk} not found."]}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "data": SuccessStorySerializer(instance).data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return Response({"success": False, "errors": [f"Success story {pk} not found."]}, status=status.HTTP_404_NOT_FOUND)
        serializer = SuccessStorySerializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        updated = serializer.save()
        return Response(
            {"success": True, "message": "Success story updated successfully.", "data": SuccessStorySerializer(updated).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        return self.patch(request, pk)

    def delete(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return Response({"success": False, "errors": [f"Success story {pk} not found."]}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response({"success": True, "message": f"Success story {pk} deleted successfully."}, status=status.HTTP_200_OK)


# =====================================================================
# 6. TEAM MEMBERS CRUD
# =====================================================================

class TeamMemberListCreateView(APIView):
    """
    GET /api/about-us/team/
    List team members.

    POST /api/about-us/team/
    Create new team member. (Admin only)
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        is_admin = request.user and request.user.is_staff
        if is_admin and request.query_params.get('all') == 'true':
            queryset = TeamMember.objects.all().order_by('display_order', 'id')
        else:
            queryset = TeamMember.objects.filter(is_active=True).order_by('display_order', 'id')
        serializer = TeamMemberSerializer(queryset, many=True)
        return Response(
            {"success": True, "count": queryset.count(), "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = TeamMemberSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(
            {"success": True, "message": "Team member created successfully.", "data": TeamMemberSerializer(instance).data},
            status=status.HTTP_201_CREATED,
        )


class TeamMemberDetailView(APIView):
    """
    GET /api/about-us/team/<id>/
    Retrieve single team member.

    PUT/PATCH /api/about-us/team/<id>/
    Update team member. (Admin only)

    DELETE /api/about-us/team/<id>/
    Delete team member. (Admin only)
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_object(self, pk):
        try:
            return TeamMember.objects.get(pk=pk)
        except TeamMember.DoesNotExist:
            return None

    def get(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return Response({"success": False, "errors": [f"Team member {pk} not found."]}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "data": TeamMemberSerializer(instance).data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return Response({"success": False, "errors": [f"Team member {pk} not found."]}, status=status.HTTP_404_NOT_FOUND)
        serializer = TeamMemberSerializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        updated = serializer.save()
        return Response(
            {"success": True, "message": "Team member updated successfully.", "data": TeamMemberSerializer(updated).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        return self.patch(request, pk)

    def delete(self, request, pk):
        instance = self.get_object(pk)
        if not instance:
            return Response({"success": False, "errors": [f"Team member {pk} not found."]}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response({"success": True, "message": f"Team member {pk} deleted successfully."}, status=status.HTTP_200_OK)
