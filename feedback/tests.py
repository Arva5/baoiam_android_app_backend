from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Feedback

User = get_user_model()


class FeedbackAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="tester@example.com",
            name="Test User",
            password="TestPass123!",
            email_verified=True,
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )
        self.url = "/api/feedback/"
        self.valid_payload = {
            "rating": 5,
            "experience": "excellent",
            "feedback": "Great app!",
        }

    # --- Auth ---
    def test_unauthenticated_returns_401(self):
        self.client.credentials()
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Happy path ---
    def test_valid_submission_returns_201(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Thank you for your feedback!")
        self.assertEqual(Feedback.objects.count(), 1)
        fb = Feedback.objects.first()
        self.assertEqual(fb.user, self.user)
        self.assertEqual(fb.rating, 5)
        self.assertEqual(fb.experience, "excellent")

    def test_feedback_text_is_optional(self):
        payload = {"rating": 3, "experience": "okay"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # --- Rating validation ---
    def test_rating_zero_is_invalid(self):
        payload = {**self.valid_payload, "rating": 0}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating", response.data)

    def test_rating_six_is_invalid(self):
        payload = {**self.valid_payload, "rating": 6}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rating", response.data)

    # --- Experience validation ---
    def test_invalid_experience_is_rejected(self):
        payload = {**self.valid_payload, "experience": "amazing"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("experience", response.data)

    def test_all_valid_experience_choices_accepted(self):
        for choice in ("excellent", "good", "okay", "bad", "poor"):
            payload = {**self.valid_payload, "experience": choice}
            response = self.client.post(self.url, payload, format="json")
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                msg=f"Failed for experience='{choice}'",
            )

    # --- Feedback text validation ---
    def test_feedback_exceeding_500_chars_is_rejected(self):
        payload = {**self.valid_payload, "feedback": "x" * 501}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("feedback", response.data)

    def test_feedback_exactly_500_chars_is_accepted(self):
        payload = {**self.valid_payload, "feedback": "x" * 500}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
