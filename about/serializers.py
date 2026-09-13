from rest_framework import serializers
from .models import AboutOverview, ImpactStat, WhyChooseUsItem, SuccessStory, TeamMember


class ImpactStatSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = ImpactStat
        fields = ['id', 'value', 'label', 'icon', 'display_order', 'is_active']

    def get_id(self, obj):
        return str(obj.id)


class WhyChooseUsItemSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = WhyChooseUsItem
        fields = ['id', 'title', 'description', 'icon', 'display_order', 'is_active']

    def get_id(self, obj):
        return str(obj.id)


class SuccessStorySerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = SuccessStory
        fields = ['id', 'name', 'role', 'rating', 'story', 'image_url', 'display_order', 'is_active']

    def get_id(self, obj):
        return str(obj.id)


class SuccessStorySubmitSerializer(serializers.ModelSerializer):
    """
    Serializer for learners/students submitting a testimonial from app.
    is_active defaults to False until reviewed/approved by admin.
    """
    name = serializers.CharField(max_length=150, trim_whitespace=True)
    role = serializers.CharField(max_length=150, trim_whitespace=True)
    rating = serializers.IntegerField(min_value=1, max_value=5, default=5)
    story = serializers.CharField(trim_whitespace=True)

    class Meta:
        model = SuccessStory
        fields = ['id', 'name', 'role', 'rating', 'story', 'image_url']
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['is_active'] = False  # requires admin approval
        return super().create(validated_data)


class TeamMemberSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = TeamMember
        fields = ['id', 'name', 'role', 'bio', 'image_url', 'display_order', 'is_active']

    def get_id(self, obj):
        return str(obj.id)


class AboutOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutOverview
        fields = [
            'id',
            'title',
            'subtitle',
            'mission_text',
            'vision_text',
            'trusted_by_labels',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# Client representation serializers matching Android AboutUsUiState
class AndroidImpactStatSerializer(serializers.Serializer):
    id = serializers.CharField()
    value = serializers.CharField()
    label = serializers.CharField()
    icon = serializers.CharField()


class AndroidWhyChooseUsItemSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    icon = serializers.CharField()


class AndroidSuccessStorySerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    role = serializers.CharField()
    rating = serializers.IntegerField()
    story = serializers.CharField()


class AndroidTeamMemberSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    role = serializers.CharField()


class AboutUsScreenDataSerializer(serializers.Serializer):
    """
    Direct 1-to-1 representation of Kotlin AboutUsUiState.
    Supports both camelCase and snake_case for maximum client compatibility.
    """
    missionText = serializers.CharField()
    impactStats = AndroidImpactStatSerializer(many=True)
    whatWeOffer = AndroidWhyChooseUsItemSerializer(many=True)
    successStories = AndroidSuccessStorySerializer(many=True)
    teamMembers = AndroidTeamMemberSerializer(many=True)
    trustedByLabels = serializers.ListField(child=serializers.CharField())

    # snake_case alternatives so Android developer can parse either
    mission_text = serializers.CharField(required=False)
    impact_stats = AndroidImpactStatSerializer(many=True, required=False)
    what_we_offer = AndroidWhyChooseUsItemSerializer(many=True, required=False)
    success_stories = AndroidSuccessStorySerializer(many=True, required=False)
    team_members = AndroidTeamMemberSerializer(many=True, required=False)
    trusted_by_labels = serializers.ListField(child=serializers.CharField(), required=False)
