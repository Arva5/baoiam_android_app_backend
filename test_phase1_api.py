"""
Manual end-to-end API test for Phase 1 (courses + enrollments).
Run with: python3 manage.py shell -c "exec(open('test_phase1_api.py').read())"
Uses Django's test Client to hit real URL-resolved views (real request/response
cycle, just no actual socket) against a throwaway sqlite DB.
"""
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from courses.models import Course, CourseModule, Lesson, ContentItem
from enrollments.models import Enrollment
import json

User = get_user_model()
client = Client()

PASS = 0
FAIL = 0

def check(label, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}  {extra}")

def jprint(resp):
    try:
        return json.dumps(resp.json(), indent=2)[:600]
    except Exception:
        return resp.content[:300]

print("=" * 70)
print("SETUP: creating test users + course data")
print("=" * 70)

# Clean slate
User.objects.filter(email__in=["student@test.com", "student2@test.com"]).delete()
Course.objects.filter(slug__in=["ui-ux-design", "draft-course"]).delete()

student = User.objects.create_user(email="student@test.com", password="testpass123", name="Test Student")
student.email_verified = True
student.save()

student2 = User.objects.create_user(email="student2@test.com", password="testpass123", name="Second Student")
student2.email_verified = True
student2.save()

instructor = User.objects.create_user(email="instructor@test.com", password="testpass123", name="Jane Instructor")

course = Course.objects.create(
    title="UI/UX Design Fundamentals",
    short_code="UI/UX",
    description="Learn UI/UX from scratch",
    thumbnail_url="https://example.com/thumb.jpg",
    instructor=instructor,
    is_published=True,
)
module1 = CourseModule.objects.create(course=course, title="Ideation & Wireframing", order=1)
lesson1 = Lesson.objects.create(module=module1, title="Wireframing Basics", order=1, published_at="2025-05-12")
ContentItem.objects.create(lesson=lesson1, content_type="VIDEO", title="Lecture 1 Recording",
                            url="https://example.com/video1.mp4", duration_seconds=2720, order=1)
ContentItem.objects.create(lesson=lesson1, content_type="PDF", title="Lecture 1 Notes",
                            url="https://example.com/notes1.pdf", file_size_bytes=2516582, order=2)

draft_course = Course.objects.create(title="Unpublished Draft Course", short_code="DR", is_published=False)

print(f"  Created course '{course.title}' (slug={course.slug}), draft course (slug={draft_course.slug})")
print(f"  total_lectures property = {course.total_lectures} (expect 1)")

# ---- Get JWT tokens via real login endpoint ----
print()
print("=" * 70)
print("AUTH: logging in via /api/auth/login/")
print("=" * 70)
resp = client.post("/api/auth/login/", {"email": "student@test.com", "password": "testpass123"},
                    content_type="application/json")
check("login returns 200", resp.status_code == 200, resp.status_code)
token = resp.json().get("access")
check("access token present", bool(token))
auth_header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

resp2 = client.post("/api/auth/login/", {"email": "student2@test.com", "password": "testpass123"},
                     content_type="application/json")
token2 = resp2.json().get("access")
auth_header2 = {"HTTP_AUTHORIZATION": f"Bearer {token2}"}

# ---- 1. GET /api/courses/ (anonymous) ----
print()
print("=" * 70)
print("TEST 1: GET /api/courses/  (anonymous)")
print("=" * 70)
resp = client.get("/api/courses/")
print(jprint(resp))
check("status 200", resp.status_code == 200)
data = resp.json().get("data", [])
titles = [c["title"] for c in data]
check("published course listed", course.title in titles)
check("draft course NOT listed", draft_course.title not in titles)
this = next((c for c in data if c["title"] == course.title), None)
check("is_enrolled False for anon", this and this["is_enrolled"] is False)
check("total_lectures == 1", this and this["total_lectures"] == 1, this)
check("short_code present", this and this["short_code"] == "UI/UX")

# ---- 2. GET /api/courses/<slug>/ (anonymous, not enrolled) ----
print()
print("=" * 70)
print("TEST 2: GET /api/courses/<slug>/  (anonymous - should be locked)")
print("=" * 70)
resp = client.get(f"/api/courses/{course.slug}/")
print(jprint(resp))
check("status 200", resp.status_code == 200)
d = resp.json()["data"]
check("has_active_access False", d["has_active_access"] is False)
check("modules outline visible", len(d["modules"]) == 1)
lesson_data = d["modules"][0]["lessons"][0]
check("lesson locked True", lesson_data["locked"] is True)
check("content_items empty when locked", lesson_data["content_items"] == [], lesson_data)

# ---- 3. GET draft course detail (anonymous should 404) ----
print()
print("=" * 70)
print("TEST 3: GET /api/courses/<draft-slug>/ (anonymous -> 404, unpublished)")
print("=" * 70)
resp = client.get(f"/api/courses/{draft_course.slug}/")
check("status 404", resp.status_code == 404, resp.status_code)

# ---- 4. GET /api/enrollments/ without auth ----
print()
print("=" * 70)
print("TEST 4: GET /api/enrollments/  (no auth -> 401)")
print("=" * 70)
resp = client.get("/api/enrollments/")
check("status 401", resp.status_code == 401, resp.status_code)

# ---- 5. POST /api/enrollments/ (enroll student in course) ----
print()
print("=" * 70)
print("TEST 5: POST /api/enrollments/  (student enrolls in course)")
print("=" * 70)
resp = client.post("/api/enrollments/", {"course_slug": course.slug},
                    content_type="application/json", **auth_header)
print(jprint(resp))
check("status 201", resp.status_code == 201, resp.status_code)
d = resp.json()["data"]
check("status ACTIVE (model default)", d["status"] == "ACTIVE", d["status"])
check("has_active_access True", d["has_active_access"] is True)
check("course nested correctly", d["course"]["slug"] == course.slug)

# ---- 6. POST duplicate enrollment -> should fail ----
print()
print("=" * 70)
print("TEST 6: POST /api/enrollments/ again (duplicate -> 400)")
print("=" * 70)
resp = client.post("/api/enrollments/", {"course_slug": course.slug},
                    content_type="application/json", **auth_header)
check("status 400", resp.status_code == 400, resp.status_code)

# ---- 7. POST enroll in nonexistent course ----
print()
print("=" * 70)
print("TEST 7: POST /api/enrollments/ with bad slug -> 400")
print("=" * 70)
resp = client.post("/api/enrollments/", {"course_slug": "does-not-exist"},
                    content_type="application/json", **auth_header)
check("status 400", resp.status_code == 400, resp.status_code)

# ---- 8. GET /api/enrollments/ (student's own list) ----
print()
print("=" * 70)
print("TEST 8: GET /api/enrollments/  (student's enrolled list)")
print("=" * 70)
resp = client.get("/api/enrollments/", **auth_header)
print(jprint(resp))
check("status 200", resp.status_code == 200)
data = resp.json()["data"]
check("exactly 1 enrollment", len(data) == 1, len(data))

# ---- 9. GET /api/courses/<slug>/ now that student is enrolled ----
print()
print("=" * 70)
print("TEST 9: GET /api/courses/<slug>/  (as enrolled student - unlocked)")
print("=" * 70)
resp = client.get(f"/api/courses/{course.slug}/", **auth_header)
d = resp.json()["data"]
check("has_active_access True", d["has_active_access"] is True)
lesson_data = d["modules"][0]["lessons"][0]
check("lesson locked False", lesson_data["locked"] is False)
check("content_items has 2 items", len(lesson_data["content_items"]) == 2, lesson_data["content_items"])
video = next(c for c in lesson_data["content_items"] if c["content_type"] == "VIDEO")
check("duration_display formatted MM:SS", video["duration_display"] == "45:20", video["duration_display"])

# ---- 10. GET /api/courses/ as enrolled student -> is_enrolled True ----
print()
print("=" * 70)
print("TEST 10: GET /api/courses/  (as enrolled student -> is_enrolled True)")
print("=" * 70)
resp = client.get("/api/courses/", **auth_header)
this = next(c for c in resp.json()["data"] if c["slug"] == course.slug)
check("is_enrolled True", this["is_enrolled"] is True)

# ---- 11. Second student should NOT see first student's enrollment ----
print()
print("=" * 70)
print("TEST 11: GET /api/enrollments/  (second student -> empty, isolation check)")
print("=" * 70)
resp = client.get("/api/enrollments/", **auth_header2)
check("status 200", resp.status_code == 200)
check("empty list for unrelated student", resp.json()["data"] == [], resp.json()["data"])

# ---- 12. GET /api/enrollments/<course_slug>/ detail ----
print()
print("=" * 70)
print("TEST 12: GET /api/enrollments/<course_slug>/  (single lookup)")
print("=" * 70)
resp = client.get(f"/api/enrollments/{course.slug}/", **auth_header)
check("status 200", resp.status_code == 200)
resp = client.get(f"/api/enrollments/{course.slug}/", **auth_header2)
check("404 for student not enrolled", resp.status_code == 404, resp.status_code)

# ---- 13. EXPIRED access check ----
print()
print("=" * 70)
print("TEST 13: Expired enrollment -> has_active_access False, content locked")
print("=" * 70)
from django.utils import timezone
from datetime import timedelta
enr = Enrollment.objects.get(user=student, course=course)
enr.access_expires_at = timezone.now() - timedelta(days=1)
enr.save()
resp = client.get(f"/api/courses/{course.slug}/", **auth_header)
d = resp.json()["data"]
check("has_active_access False after expiry", d["has_active_access"] is False)
resp = client.get(f"/api/enrollments/{course.slug}/", **auth_header)
check("has_active_access False in enrollment detail too", resp.json()["data"]["has_active_access"] is False)

print()
print("=" * 70)
print(f"RESULT: {PASS} passed, {FAIL} failed")
print("=" * 70)
