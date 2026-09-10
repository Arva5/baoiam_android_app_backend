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

    def test_attempt_uses_configured_auth_user_model(self):
        self.assertIs(UserAssessmentAttempt._meta.get_field('user').remote_field.model, User)
        self.assertEqual(UserAssessmentAttempt._meta.get_field('user').remote_field.model._meta.db_table, 'accounts_user')

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
        self.assertEqual(response.data['detail'], 'Quiz completed successfully.')
        self.assertIn('attempt_id', response.data)
        self.assertIn('completed_at', response.data)
        self.assertIn('recommended_courses', response.data)
        self.assertIsInstance(response.data['recommended_courses'], list)

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


class CourseDiscoveryQuizTests(APITestCase):
    def setUp(self):
        from django.core.management import call_command
        from courses.models import Category, Course

        self.user = User.objects.create_user(
            email='discover@example.com',
            name='Discover User',
            password='Password123!',
        )
        call_command('seed_discovery_quiz', verbosity=0)

        self.web_cat, _ = Category.objects.get_or_create(
            slug='web-development', defaults={'name': 'Web Development'}
        )
        self.dev_cat, _ = Category.objects.get_or_create(
            slug='development', defaults={'name': 'Development'}
        )
        self.tech_cat, _ = Category.objects.get_or_create(
            slug='technology', defaults={'name': 'Technology'}
        )

        self.beginner_web = Course.objects.create(
            title='Intro to HTML and CSS',
            category=self.web_cat,
            level='beginner',
            is_published=True,
            rating=4.9,
        )
        self.all_levels_web = Course.objects.create(
            title='Full Stack Web Bootcamp',
            category=self.web_cat,
            level='all_levels',
            is_published=True,
            rating=4.7,
        )
        self.unpublished_web = Course.objects.create(
            title='Secret Web Course',
            category=self.web_cat,
            level='beginner',
            is_published=False,
        )
        self.dev_fallback = Course.objects.create(
            title='Software Engineering Path',
            category=self.dev_cat,
            level='beginner',
            is_published=True,
        )
        self.data_course = Course.objects.create(
            title='Python Data Analytics',
            category=self.tech_cat,
            level='intermediate',
            is_published=True,
        )

    def _quiz(self):
        return Assessment.objects.get(title='Course Discovery Quiz')

    def _answers(self, interest='Web Development', experience='Complete Beginner'):
        quiz = self._quiz()
        answers = {}
        wanted = {
            1: interest,
            2: '2-5 hours',
            3: experience,
            4: 'Skill Upgrade',
            5: 'Mixed Approach',
        }
        for question in quiz.questions.filter(is_active=True):
            option = question.options.get(option_text=wanted[question.order])
            answers[str(question.id)] = option.id
        return quiz, answers

    def test_seed_command_is_idempotent(self):
        from django.core.management import call_command

        call_command('seed_discovery_quiz', verbosity=0)
        self.assertEqual(Assessment.objects.filter(title='Course Discovery Quiz').count(), 1)
        quiz = self._quiz()
        self.assertEqual(quiz.questions.filter(is_active=True).count(), 5)
        for question in quiz.questions.filter(is_active=True):
            self.assertEqual(question.options.count(), 4)

    def test_featured_quiz_returns_discovery_questions(self):
        response = self.client.get(reverse('featured-quiz'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Course Discovery Quiz')
        self.assertEqual(len(response.data['questions']), 5)
        first = response.data['questions'][0]
        self.assertEqual(
            first['question_text'],
            'What type of programming are you most interested in?',
        )
        self.assertEqual(len(first['options']), 4)

    def test_submit_recommends_web_beginner_courses(self):
        quiz, answers = self._answers()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('submit-quiz', kwargs={'id': quiz.id}),
            {'answers': answers},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['recommended_path'], 'Web Development')
        self.assertEqual(response.data['detail'], 'Quiz completed successfully.')
        self.assertTrue(UserAssessmentAttempt.objects.filter(id=response.data['attempt_id']).exists())

        titles = [course['title'] for course in response.data['recommended_courses']]
        self.assertLessEqual(len(titles), 5)
        self.assertIn('Intro to HTML and CSS', titles)
        self.assertNotIn('Secret Web Course', titles)
        self.assertTrue(titles.index('Intro to HTML and CSS') < titles.index('Full Stack Web Bootcamp'))

    def test_submit_data_science_falls_back_to_technology(self):
        quiz, answers = self._answers(interest='Data Science', experience='Intermediate')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('submit-quiz', kwargs={'id': quiz.id}),
            {'answers': answers},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['recommended_path'], 'Data Science')
        titles = [course['title'] for course in response.data['recommended_courses']]
        self.assertIn('Python Data Analytics', titles)

    def test_submit_requires_authentication(self):
        quiz, answers = self._answers()
        response = self.client.post(
            reverse('submit-quiz', kwargs={'id': quiz.id}),
            {'answers': answers},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

