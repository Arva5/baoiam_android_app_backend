from collections import Counter
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Assessment, Option, Question, UserAssessmentAttempt
from .serializers import (
    AssessmentDetailSerializer,
    AssessmentListSerializer,
    SubmitQuizSerializer,
    UserAssessmentAttemptSerializer,
)


class AssessmentListView(generics.ListAPIView):
    serializer_class = AssessmentListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Assessment.objects.filter(is_active=True).prefetch_related('questions')
        quiz_type = self.request.query_params.get('type')
        if quiz_type:
            queryset = queryset.filter(quiz_type=quiz_type)
        return queryset


class AssessmentDetailView(generics.RetrieveAPIView):
    queryset = Assessment.objects.filter(is_active=True).prefetch_related('questions__options')
    serializer_class = AssessmentDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'


class FeaturedQuizView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        quiz = Assessment.objects.filter(
            is_active=True,
            is_featured=True
        ).prefetch_related('questions__options').first()

        if not quiz:
            quiz = Assessment.objects.filter(is_active=True).prefetch_related('questions__options').first()

        if not quiz:
            return Response(
                {"detail": "No active learning path quiz available."},
                status=status.HTTP_404_NOT_FOUND
            )

        data = AssessmentDetailSerializer(quiz).data
        if request.user.is_authenticated:
            last_attempt = UserAssessmentAttempt.objects.filter(
                user=request.user,
                assessment=quiz,
                is_completed=True
            ).order_by('-completed_at').first()
            if last_attempt:
                data['last_completed_attempt'] = {
                    'id': last_attempt.id,
                    'recommended_path': last_attempt.recommended_path,
                    'completed_at': last_attempt.completed_at,
                }
            else:
                data['last_completed_attempt'] = None
        else:
            data['last_completed_attempt'] = None

        return Response(data, status=status.HTTP_200_OK)


class SubmitAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        assessment = get_object_or_404(Assessment, id=id, is_active=True)
        serializer = SubmitQuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers = serializer.validated_data['answers']

        # Fetch all questions and their options belonging to this assessment
        questions = Question.objects.filter(
            assessment=assessment,
            is_active=True,
        ).prefetch_related('options')
        q_map = {q.id: {opt.id: opt for opt in q.options.all()} for q in questions}

        selected_options = []
        validated_answers = {}
        for q_id_raw, opt_id in answers.items():
            try:
                q_id = int(q_id_raw)
            except (ValueError, TypeError):
                return Response(
                    {"answers": f"Invalid question ID format: '{q_id_raw}'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if q_id not in q_map:
                return Response(
                    {"answers": f"Question {q_id} does not belong to this assessment or does not exist."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if q_id in validated_answers:
                return Response(
                    {"answers": f"Question {q_id} was answered more than once."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            valid_options = q_map[q_id]
            if opt_id not in valid_options:
                return Response(
                    {"answers": f"Option {opt_id} is not a valid option for question {q_id}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            selected_options.append(valid_options[opt_id])
            validated_answers[q_id] = opt_id

        missing_question_ids = set(q_map).difference(validated_answers)
        if missing_question_ids:
            return Response(
                {"answers": "An answer is required for every question in this assessment."},
                status=status.HTTP_400_BAD_REQUEST
            )

        answers = {str(q_id): opt_id for q_id, opt_id in validated_answers.items()}

        recommended_path = self._determine_recommended_path(
            questions=questions,
            q_map=q_map,
            answers=answers,
            selected_options=selected_options,
        )

        attempt = UserAssessmentAttempt.objects.create(
            user=request.user,
            assessment=assessment,
            selected_answers=answers,
            recommended_path=recommended_path,
            is_completed=True,
            completed_at=timezone.now(),
        )

        recommended_courses = self._get_recommended_courses(
            questions=questions,
            q_map=q_map,
            answers=answers,
            request=request,
        )

        return Response({
            'detail': 'Quiz completed successfully.',
            'attempt_id': attempt.id,
            'recommended_path': recommended_path,
            'completed_at': attempt.completed_at,
            'recommended_courses': recommended_courses,
        }, status=status.HTTP_201_CREATED)

    # ------------------------------------------------------------------ #
    # Recommendation helpers                                               #
    # ------------------------------------------------------------------ #

    # Q1 career_track → display label for recommended_path
    _PATH_LABELS = {
        "web": "Web Development",
        "mobile": "Mobile Development",
        "data": "Data Science",
        "game": "Game Development",
    }

    # Q1 career_track → keywords to match category slug/name and course title
    _INTEREST_KEYWORDS = {
        "web": ["web", "full-stack", "fullstack", "frontend", "backend", "javascript", "html", "css"],
        "mobile": ["mobile", "android", "ios", "flutter", "react-native"],
        "data": ["data", "machine-learning", "ai", "python", "analytics", "ml", "deep-learning"],
        "game": ["game", "unity", "unreal", "gaming", "gamedev"],
    }

    # Broader existing categories (Development, Technology) when no specific match exists
    _INTEREST_FALLBACK_KEYWORDS = {
        "web": ["development"],
        "mobile": ["development"],
        "data": ["technology"],
        "game": ["development"],
    }

    # Q3 option_text → Course.level value
    _EXPERIENCE_LEVEL_MAP = {
        "Complete Beginner": "beginner",
        "Some Experience": "beginner",
        "Intermediate": "intermediate",
        "Advanced": "advanced",
    }

    def _selected_option(self, question, q_map, answers):
        if not question:
            return None
        opt_id = answers.get(str(question.id))
        if opt_id is None:
            opt_id = answers.get(question.id)
        if opt_id and opt_id in q_map.get(question.id, {}):
            return q_map[question.id][opt_id]
        return None

    def _determine_recommended_path(self, questions, q_map, answers, selected_options):
        q_by_order = {q.order: q for q in questions}
        q1_option = self._selected_option(q_by_order.get(1), q_map, answers)
        if q1_option and q1_option.career_track:
            return self._PATH_LABELS.get(q1_option.career_track, q1_option.career_track)

        track_counts = Counter(opt.career_track for opt in selected_options if opt.career_track)
        if track_counts:
            return track_counts.most_common(1)[0][0]
        return "Full Stack Web & Mobile Development"

    def _get_recommended_courses(self, questions, q_map, answers, request):
        """Return up to 5 serialized published courses based on Q1 (interest) and Q3 (level)."""
        from django.db.models import Q

        from courses.models import Course
        from courses.serializers import CourseSerializer

        q_by_order = {q.order: q for q in questions}

        interest_track = None
        q1_option = self._selected_option(q_by_order.get(1), q_map, answers)
        if q1_option:
            interest_track = q1_option.career_track or None

        experience_level = None
        q3_option = self._selected_option(q_by_order.get(3), q_map, answers)
        if q3_option:
            experience_level = self._EXPERIENCE_LEVEL_MAP.get(q3_option.option_text)

        base_qs = Course.objects.filter(is_published=True).select_related('category')
        recommended = []
        already_ids = set()

        def add_from(queryset):
            remaining = 5 - len(recommended)
            if remaining <= 0:
                return
            for course in queryset.exclude(id__in=already_ids)[:remaining]:
                recommended.append(course)
                already_ids.add(course.id)

        specific_q = self._keyword_q(interest_track, self._INTEREST_KEYWORDS)
        fallback_q = self._keyword_q(interest_track, self._INTEREST_FALLBACK_KEYWORDS)

        if specific_q is not None and experience_level:
            add_from(base_qs.filter(specific_q).filter(level=experience_level))
        if specific_q is not None:
            add_from(base_qs.filter(specific_q).filter(level='all_levels'))
            add_from(base_qs.filter(specific_q))
        if fallback_q is not None and experience_level:
            add_from(base_qs.filter(fallback_q).filter(Q(level=experience_level) | Q(level='all_levels')))
            add_from(base_qs.filter(fallback_q))
        add_from(base_qs.order_by('-rating', '-is_featured'))

        return CourseSerializer(recommended, many=True, context={'request': request}).data

    def _keyword_q(self, interest_track, keyword_map):
        from django.db.models import Q

        keywords = keyword_map.get(interest_track or '', [])
        if not keywords:
            return None
        query = Q()
        for kw in keywords:
            query |= (
                Q(category__slug__icontains=kw)
                | Q(category__name__icontains=kw)
                | Q(title__icontains=kw)
            )
        return query


class UserAttemptsListView(generics.ListAPIView):
    serializer_class = UserAssessmentAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAssessmentAttempt.objects.filter(user=self.request.user).select_related('assessment')
