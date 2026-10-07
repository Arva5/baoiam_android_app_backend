# Baoiam Android APIs

Base URL (local): `http://<YOUR_PC_IP>:8000`  
Emulator: `http://10.0.2.2:8000`

Auth header (jab API Auth = Yes ho):

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

Login ke baad `access` token save karo. 401 aaye to `POST /api/auth/token/refresh/` se naya access lo.

---

## Video flow (course list → details → play)

1. `GET /api/courses/` — course list (modules locked until enroll).
2. `GET /api/courses/{id}/` — course details.
3. Free dummy courses: `POST /api/courses/{id}/enroll/` with Bearer token.
4. Dobara details hit karo — `content_items[].url` milega.
5. **Play URL (recommended):** `GET /api/courses/content/{content_id}/play/`  
   Response me `url` aata hai. Isi URL ko ExoPlayer / VideoView me play karo (`video/mp4`).

Locked lesson: `locked: true`, `content_items: []`. Video URL tabhi aati hai jab user enrolled ho.

---

## Auth

| Method | Path | Auth | Body |
|--------|------|------|------|
| POST | `/api/auth/signup/` | No | `{ "name", "email", "password", "confirm_password", "agree_to_terms" }` |
| POST | `/api/auth/verify-email/` | No | `{ "email", "otp" }` |
| POST | `/api/auth/resend-otp/` | No | `{ "email" }` |
| POST | `/api/auth/login/` | No | `{ "email", "password", "remember_me"? }` → `{ access, refresh }` |
| POST | `/api/auth/google/` | No | `{ "id_token" }` |
| POST | `/api/auth/logout/` | Yes | `{ "refresh" }` |
| POST | `/api/auth/token/refresh/` | No | `{ "refresh" }` |
| POST | `/api/auth/forgot-password/` | No | `{ "email" }` |
| POST | `/api/auth/reset-password/` | No | `{ "reset_token", "new_password", "confirm_password" }` |
| GET/PATCH | `/api/auth/me/` | Yes | profile |
| GET/PATCH | `/api/users/me/` | Yes | same current user |
| GET/PATCH | `/api/auth/profile/` | Yes | |
| POST | `/api/auth/profile-setup/` | Yes | |
| GET/PATCH | `/api/auth/personal-info/` | Yes | |
| POST | `/api/auth/delete-account/` | Yes | |

---

## Courses (list, details, video)

| Method | Path | Auth | Notes |
|--------|------|------|--------|
| GET | `/api/courses/` | No | Query: `search`, `category`, `is_featured`, `level`, `include_modules=false` |
| GET | `/api/courses/{id}/` | No | Detail by id |
| GET | `/api/courses/{slug}/` | No | Detail by slug |
| POST | `/api/courses/{id}/enroll/` | Yes | Free course enroll. Paid → 402 |
| POST | `/api/courses/{slug}/enroll/` | Yes | |
| GET | `/api/courses/content/{content_id}/play/` | Yes | **Video/PDF URL.** 403 if not enrolled |
| GET | `/api/courses/categories/` | No | |
| GET | `/api/courses/promotions/` | No | |
| GET | `/api/courses/tip-of-the-day/` | No | |
| GET | `/api/courses/why-choose-us/` | No | |
| GET | `/api/courses/my-enrollments/` | Yes | |

### Course list item (important fields)

`id`, `title`, `slug`, `short_code`, `subtitle`, `description`, `thumbnail_url`, `cover_image_url`, `instructor_name`, `category`, `category_name`, `level`, `rating`, `duration_hours`, `lessons_count`, `total_lectures`, `price`, `discounted_price`, `is_featured`, `is_popular`, `is_enrolled`, `has_active_access`, `modules`

### Nested (enrolled)

```json
{
  "modules": [
    {
      "id": 1,
      "title": "Introduction",
      "order": 1,
      "lessons": [
        {
          "id": 10,
          "title": "Welcome to the course",
          "locked": false,
          "content_items": [
            {
              "id": 100,
              "content_type": "VIDEO",
              "title": "Welcome Video",
              "url": "https://....mp4",
              "play_url": "https://....mp4",
              "duration_seconds": 596,
              "duration_display": "9:56"
            }
          ]
        }
      ]
    }
  ]
}
```

### Play response

```json
{
  "content_id": 100,
  "lesson_id": 10,
  "course_id": 1,
  "course_slug": "python-for-beginners",
  "content_type": "VIDEO",
  "title": "Welcome Video",
  "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
  "play_url": "https://....mp4",
  "mime_type": "video/mp4",
  "duration_seconds": 596,
  "duration_display": "9:56"
}
```

Android: `ExoPlayer` me `MediaItem.fromUri(url)` use karo.

---

## Enrollments (My Learning)

| Method | Path | Auth | Body |
|--------|------|------|------|
| GET | `/api/enrollments/` | Yes | `{ success, data }` |
| POST | `/api/enrollments/` | Yes | `{ "course_slug": "python-for-beginners" }` |
| GET | `/api/enrollments/{course_slug}/` | Yes | |

---

## Home

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/home/` | check view (often any) |
| GET | `/api/home/screen1/` | |
| GET | `/api/home/engagement/` | |
| GET | `/api/home/getting-started/` | |
| GET | `/api/home/promotional-banners/` | |
| GET | `/api/home/learning-path-quiz/` | |
| GET | `/api/home/why-choose-us/` | |
| GET | `/api/home/tip-of-the-day/` | |
| GET | `/api/home/start-your-journey/` | |
| GET | `/api/home/notifications/` | Yes |
| GET | `/api/home/notifications/unread-count/` | Yes |
| POST | `/api/home/notifications/read-all/` | Yes |
| PATCH | `/api/home/notifications/{id}/read/` | Yes |

Same notification APIs: `/api/notifications/`

---

## Assessments

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/assessments/` | |
| GET | `/api/assessments/featured-quiz/` | |
| GET | `/api/assessments/{id}/` | |
| POST | `/api/assessments/{id}/submit/` | Yes |
| GET | `/api/assessments/my-attempts/` | Yes |

---

## Certificates

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/certificates/` | |
| GET | `/api/certificates/{id}/` | |
| GET | `/api/certificates/my-certificates/` | Yes |
| GET | `/api/certificates/verify/{certificate_code}/` | No |

---

## Legal, feedback, contact, about, issues

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/legal/{doc_type}/` | |
| POST | `/api/legal/accept/` | Yes |
| POST | `/api/feedback/` | Yes |
| GET | `/api/contact/` | No |
| POST | `/api/contact/message/` | |
| GET | `/api/contact/questions/` | No |
| GET | `/api/about-us/` | No |
| POST | `/api/about-us/stories/submit/` | |
| POST | `/api/issues/report/` | Yes |

---

## Dummy courses (after seed)

| Title | Slug | Price |
|-------|------|-------|
| Python for Beginners | `python-for-beginners` | 0 (free enroll) |
| Android Development with Kotlin | `android-development-with-kotlin` | 0 |
| UI/UX Design Basics | `uiux-design-basics` | 0 |
