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
        questions = Question.objects.filter(assessment=assessment).prefetch_related('options')
        q_map = {q.id: {opt.id: opt for opt in q.options.all()} for q in questions}

        selected_options = []
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

            valid_options = q_map[q_id]
            if opt_id not in valid_options:
                return Response(
                    {"answers": f"Option {opt_id} is not a valid option for question {q_id}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            selected_options.append(valid_options[opt_id])

        # Determine recommended track by collecting career_track from verified options
        track_counts = Counter(opt.career_track for opt in selected_options if opt.career_track)
        recommended_path = track_counts.most_common(1)[0][0] if track_counts else "Full Stack Web & Mobile Development"

        attempt = UserAssessmentAttempt.objects.create(
            user=request.user,
            assessment=assessment,
            selected_answers=answers,
            recommended_path=recommended_path,
            is_completed=True,
            completed_at=timezone.now(),
        )

        return Response({
            'detail': 'Quiz completed successfully.',
            'attempt_id': attempt.id,
            'recommended_path': recommended_path,
            'completed_at': attempt.completed_at,
        }, status=status.HTTP_201_CREATED)



class UserAttemptsListView(generics.ListAPIView):
    serializer_class = UserAssessmentAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAssessmentAttempt.objects.filter(user=self.request.user).select_related('assessment')
