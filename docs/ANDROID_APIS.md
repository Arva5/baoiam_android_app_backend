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

## Courses (list, details, video, bookmark)

| Method | Path | Auth | Notes |
|--------|------|------|--------|
| GET | `/api/courses/` | No | Query: `search`, `category`, `is_featured`, `level`, `include_drafts=true` |
| GET | `/api/courses/{id}/` | No | Detail by id (e.g. `/api/courses/9/`) |
| GET | `/api/courses/{slug}/` | No | Detail by slug |
| POST | `/api/courses/{id}/enroll/` | Yes | Free course enroll. Paid → 402 |
| POST | `/api/courses/{id}/save/` | Yes | Bookmark/Save course for current user |
| DELETE | `/api/courses/{id}/save/` | Yes | Remove bookmark/save |
| GET | `/api/courses/saved/` | Yes | List all bookmarked courses |
| GET | `/api/courses/lessons/{id}/play/` | Optional | Play lecture video URL. Previews are free (no auth required)! |
| GET | `/api/courses/content/{content_id}/play/` | Yes | **Legacy ContentItem play URL.** 403 if not enrolled |
| GET | `/api/courses/categories/` | No | List of course categories |
| GET | `/api/courses/promotions/` | No | Promotional banners |
| GET | `/api/courses/tip-of-the-day/` | No | Daily tip |
| GET | `/api/courses/why-choose-us/` | No | Value propositions |
| GET | `/api/courses/my-enrollments/` | Yes | Current user's enrollments |

### Course detail response (`GET /api/courses/9/`)

```json
{
  "id": 9,
  "title": "Full Stack JavaScript",
  "subtitle": "MERN stack development",
  "description": "Master MongoDB, Express, React, and Node.js. Build complete full-stack web applications from scratch with modern best practices, state management, and cloud deployment.",
  "thumbnail_url": "https://images.unsplash.com/photo-1579468118864-1b9ea3c0db4a?auto=format&fit=crop&w=800&q=80",
  "cover_image_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=1200&q=80",
  "instructor": 1,
  "instructor_name": "Sarah Johnson",
  "category": 3,
  "category_name": "Technology",
  "level": "intermediate",
  "rating": "4.50",
  "reviews_count": 342,
  "duration_hours": "60.0",
  "lessons_count": 150,
  "total_lectures": 150,
  "price": "129.99",
  "discounted_price": "89.99",
  "is_enrolled": false,
  "is_saved": false,
  "what_you_learn": [
    "Build full-stack web applications with React, Node.js, Express, and MongoDB",
    "Design RESTful APIs, implement authentication with JWT and role-based authorization",
    "State management with Redux Toolkit and React Query",
    "Deploy applications with CI/CD on Cloudflare and AWS"
  ],
  "key_features": [
    "60.0 hours on-demand high-definition video",
    "150 comprehensive lectures and code repositories",
    "Industry-recognized Certificate of Completion",
    "Direct access to mentor Q&A forum",
    "Full lifetime access on mobile and web"
  ],
  "modules": [
    {
      "id": 1,
      "title": "Module 1: Modern JavaScript & ES6+ Mastery",
      "order": 1,
      "lectures": [
        {
          "id": 23,
          "title": "Welcome to Full Stack JavaScript",
          "description": "Course overview, roadmap, and local development environment setup.",
          "order": 1,
          "duration": "10:30",
          "duration_seconds": 630,
          "video_url": "https://pub-xxxxxxxx.r2.dev/videos/javascript/welcome.mp4",
          "thumbnail_url": "https://images.unsplash.com/photo-1579468118864-1b9ea3c0db4a?auto=format&fit=crop&w=640&q=80",
          "is_preview": true,
          "locked": false
        }
      ]
    }
  ]
}
```

### Android ExoPlayer Video Playback (Kotlin)

```kotlin
// Video playback code for Android Developer:
val player = ExoPlayer.Builder(context).build()
playerView.player = player

// Play from lecture.video_url directly or from /api/courses/lessons/{id}/play/
val mediaItem = MediaItem.fromUri(lecture.videoUrl)
player.setMediaItem(mediaItem)
player.prepare()
player.playWhenReady = true
```

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
