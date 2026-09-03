from rest_framework import serializers


class GettingStartedStepSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    is_completed = serializers.BooleanField()
    action_type = serializers.CharField()
    action_url = serializers.CharField()


class GettingStartedSerializer(serializers.Serializer):
    title = serializers.CharField()
    subtitle = serializers.CharField()
    progress_percentage = serializers.IntegerField()
    completed_steps_count = serializers.IntegerField()
    total_steps_count = serializers.IntegerField()
    is_completed = serializers.BooleanField()
    steps = GettingStartedStepSerializer(many=True)


class PromotionalBannerHomeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subtitle = serializers.CharField(allow_blank=True)
    tagline = serializers.CharField(allow_blank=True)
    image_url = serializers.URLField(allow_null=True)
    badge_text = serializers.CharField(allow_blank=True)
    discount_code = serializers.CharField(allow_blank=True)
    discount_percentage = serializers.IntegerField()
    target_type = serializers.CharField()
    target_id = serializers.CharField(allow_blank=True)
    target_url = serializers.URLField(allow_null=True)
    button_text = serializers.CharField()
    start_date = serializers.DateTimeField(allow_null=True)
    end_date = serializers.DateTimeField(allow_null=True)


class QuizInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subtitle = serializers.CharField(allow_blank=True)
    description = serializers.CharField(allow_blank=True)
    thumbnail_url = serializers.URLField(allow_null=True)
    quiz_type = serializers.CharField()
    estimated_minutes = serializers.IntegerField()
    questions_count = serializers.IntegerField()
    badge_text = serializers.CharField(allow_blank=True)


class QuizUserStatusSerializer(serializers.Serializer):
    has_attempted = serializers.BooleanField()
    attempt_id = serializers.IntegerField(allow_null=True)
    recommended_path = serializers.CharField(allow_null=True)
    completed_at = serializers.DateTimeField(allow_null=True)


class LearningPathQuizHomeSerializer(serializers.Serializer):
    is_available = serializers.BooleanField()
    quiz = QuizInfoSerializer(allow_null=True)
    user_status = QuizUserStatusSerializer(allow_null=True)


class WhyChooseUsItemHomeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    icon_url = serializers.URLField(allow_null=True)
    icon_name = serializers.CharField(allow_blank=True)
    highlight_stat = serializers.CharField(allow_blank=True)


class WhyChooseUsHomeSerializer(serializers.Serializer):
    title = serializers.CharField()
    subtitle = serializers.CharField()
    items = WhyChooseUsItemHomeSerializer(many=True)


class TipOfTheDayHomeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    category = serializers.CharField()
    author_name = serializers.CharField()
    author_avatar_url = serializers.URLField(allow_null=True)
    icon_name = serializers.CharField(allow_blank=True)
    publish_date = serializers.DateField(allow_null=True)
    likes_count = serializers.IntegerField()


class ResumeCourseSerializer(serializers.Serializer):
    enrollment_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    course_thumbnail_url = serializers.URLField(allow_null=True)
    category_name = serializers.CharField(allow_null=True)
    progress_percentage = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    total_lessons = serializers.IntegerField()
    current_lesson_title = serializers.CharField(allow_blank=True)
    last_accessed_at = serializers.DateTimeField()


class CertificateInfoSerializer(serializers.Serializer):
    certificate_code = serializers.CharField()
    title = serializers.CharField()
    issued_at = serializers.DateTimeField()
    badge_icon_url = serializers.URLField(allow_null=True)



class StarterCourseSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    title = serializers.CharField()
    subtitle = serializers.CharField(allow_blank=True)
    thumbnail_url = serializers.URLField(allow_null=True)
    level = serializers.CharField()
    duration_hours = serializers.DecimalField(max_digits=5, decimal_places=1)
    rating = serializers.CharField()


class StartYourJourneyHomeSerializer(serializers.Serializer):
    journey_state = serializers.CharField()
    is_authenticated = serializers.BooleanField()
    headline = serializers.CharField()
    subheadline = serializers.CharField()
    enrolled_courses_count = serializers.IntegerField()
    completed_courses_count = serializers.IntegerField()
    certificates_earned_count = serializers.IntegerField()
    primary_resume_course = ResumeCourseSerializer(allow_null=True)
    latest_certificate = CertificateInfoSerializer(allow_null=True)
    next_milestone = serializers.CharField()
    recommended_starter_course = StarterCourseSerializer(allow_null=True)


class HomeScreenEngagementSerializer(serializers.Serializer):
    getting_started = GettingStartedSerializer()
    promotional_banners = PromotionalBannerHomeSerializer(many=True)
    learning_path_quiz = LearningPathQuizHomeSerializer()
    why_choose_us = WhyChooseUsHomeSerializer()
    tip_of_the_day = TipOfTheDayHomeSerializer(allow_null=True)
    start_your_journey = StartYourJourneyHomeSerializer()
