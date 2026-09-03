from rest_framework import serializers
from .models import Assessment, Option, Question, UserAssessmentAttempt


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'option_text', 'career_track', 'order')


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'question_text', 'order', 'options')


class AssessmentListSerializer(serializers.ModelSerializer):
    questions_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Assessment
        fields = (
            'id',
            'title',
            'subtitle',
            'description',
            'thumbnail_url',
            'quiz_type',
            'estimated_minutes',
            'questions_count',
            'badge_text',
            'is_featured',
            'is_active',
        )


class AssessmentDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    questions_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Assessment
        fields = (
            'id',
            'title',
            'subtitle',
            'description',
            'thumbnail_url',
            'quiz_type',
            'estimated_minutes',
            'questions_count',
            'badge_text',
            'is_featured',
            'questions',
        )


class UserAssessmentAttemptSerializer(serializers.ModelSerializer):
    assessment_title = serializers.CharField(source='assessment.title', read_only=True)

    class Meta:
        model = UserAssessmentAttempt
        fields = (
            'id',
            'assessment',
            'assessment_title',
            'selected_answers',
            'recommended_path',
            'score',
            'is_completed',
            'completed_at',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'completed_at')


class SubmitQuizSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="Mapping of question_id to selected option_id, e.g. {'1': 3, '2': 5}"
    )

