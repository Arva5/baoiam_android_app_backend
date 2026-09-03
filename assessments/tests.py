from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from assessments.models import Assessment, Option, Question, UserAssessmentAttempt

User = get_user_model()


class AssessmentsAppTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='quizuser@example.com',
            name='Quiz Taker',
            password='Password123!',
        )
        self.quiz = Assessment.objects.create(
            title='Learning Path Finder',
            quiz_type='career_path',
            is_featured=True,
            is_active=True,
        )
        self.q1 = Question.objects.create(
            assessment=self.quiz,
            question_text='What area do you want to master?',
            order=1,
        )
        self.opt1 = Option.objects.create(
            question=self.q1,
            option_text='Backend Engineering',
            career_track='Backend Development',
            order=1,
        )

    def test_featured_quiz(self):
        url = reverse('featured-quiz')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Learning Path Finder')

    def test_submit_quiz(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('submit-quiz', kwargs={'id': self.quiz.id})
        payload = {
            'answers': {
                str(self.q1.id): self.opt1.id,
            }
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['recommended_path'], 'Backend Development')

        # Check attempts endpoint
        res_attempts = self.client.get(reverse('user-attempts'))
        self.assertEqual(res_attempts.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_attempts.data), 1)

    def test_submit_quiz_invalid_question_belongs_to_other_assessment(self):
        other_quiz = Assessment.objects.create(
            title='Other Quiz',
            is_active=True,
        )
        other_q = Question.objects.create(
            assessment=other_quiz,
            question_text='Other question?',
            order=1,
        )
        other_opt = Option.objects.create(
            question=other_q,
            option_text='Other Option',
            order=1,
        )

        self.client.force_authenticate(user=self.user)
        url = reverse('submit-quiz', kwargs={'id': self.quiz.id})
        # Try to submit other quiz's question to self.quiz
        payload = {'answers': {str(other_q.id): other_opt.id}}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_quiz_invalid_option_belongs_to_other_question(self):
        q2 = Question.objects.create(
            assessment=self.quiz,
            question_text='Question 2?',
            order=2,
        )
        opt2 = Option.objects.create(
            question=q2,
            option_text='Option 2',
            order=1,
        )

        self.client.force_authenticate(user=self.user)
        url = reverse('submit-quiz', kwargs={'id': self.quiz.id})
        # Submit q1 with opt2 (which belongs to q2)
        payload = {'answers': {str(self.q1.id): opt2.id}}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_quiz_nonexistent_ids(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('submit-quiz', kwargs={'id': self.quiz.id})

        # Non-existent question
        response = self.client.post(url, {'answers': {'99999': self.opt1.id}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Non-existent option
        response = self.client.post(url, {'answers': {str(self.q1.id): 99999}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Empty answers
        response = self.client.post(url, {'answers': {}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

