# Baoiam Backend APIs + Cloudflare video

Android ko **playable URL** Django se milti hai. Videos Cloudflare R2 pe store karo (ya dummy Google sample MP4). Backend `ContentItem.url` / `storage_key` se URL resolve karta hai.

---

## Local setup

```bash
cd baoiam_android_app_backend
python manage.py migrate
python manage.py seed_dummy_courses --reset
python manage.py runserver 0.0.0.0:8000
```

Dummy seed **free** courses + sample MP4 URLs lagata hai (Android turant play kar sakta hai, R2 ke bina).

Optional test enroll:

```bash
python manage.py seed_dummy_courses --reset --enroll-email student@test.com
```

---

## Cloudflare R2 pe dummy videos save

1. Cloudflare login: `npx wrangler login`
2. Upload:

```bash
python scripts/upload_dummy_videos_to_r2.py
```

3. Dashboard → R2 bucket `baoiam-course-videos` → **Public Development URL** enable.
4. `.env`:

```
R2_BUCKET_NAME=baoiam-course-videos
R2_PUBLIC_BASE_URL=https://pub-xxxxxxxx.r2.dev
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
```

5. DB me R2 URLs seed:

```bash
python manage.py seed_dummy_courses --reset --r2-base-url https://pub-xxxxxxxx.r2.dev
```

Object keys (upload script + seed same):

- `videos/python/welcome.mp4`
- `videos/python/install.mp4`
- `videos/python/variables.mp4`
- `videos/android/setup.mp4`
- `videos/android/compose.mp4`
- `videos/uiux/intro.mp4`
- `videos/uiux/colors.mp4`
- `pdfs/python/cheatsheet.pdf`

Public URL = `{R2_PUBLIC_BASE_URL}/{storage_key}`

---

## URL resolve rule (`courses/storage.py`)

1. Agar `R2_PUBLIC_BASE_URL` + `ContentItem.storage_key` → R2 public URL
2. Else `ContentItem.url` (sample Google MP4)

Android kabhi R2 credentials nahi dekhta. Sirf HTTPS MP4 URL.

---

## Course endpoints (Django)

Mounted at `/api/courses/` (`config/urls.py`).

| Method | Path | Permission | Implementation |
|--------|------|------------|----------------|
| GET | `/api/courses/` | AllowAny | `CourseListView` |
| GET | `/api/courses/<id>/` | AllowAny | `CourseDetailView` |
| GET | `/api/courses/<slug>/` | AllowAny | `CourseDetailView` |
| POST | `/api/courses/<id>/enroll/` | IsAuthenticated | `CourseEnrollView` — free only; paid 402 |
| GET | `/api/courses/content/<id>/play/` | IsAuthenticated | `ContentPlayView` — playback URL |
| GET | `/api/courses/categories/` | AllowAny | |
| GET | `/api/courses/my-enrollments/` | IsAuthenticated | |

Video URL **sirf enrolled user** ko. `user_has_course_access` → `CourseEnrollment` ya `enrollments.Enrollment`.

Admin: Course → Module → Lesson → ContentItem (`url`, `storage_key`, `content_type=VIDEO`).

---

## Full API map (Android + admin)

### Auth — `/api/auth/`

signup, verify-email, resend-otp, login, google, logout, token/refresh, me, profile, profile-setup, personal-info, forgot-password, reset-password, delete-account, setup-admin

### Home — `/api/home/` and `/api/`

engagement, getting-started, banners, quiz, why-choose-us, tip, start-your-journey, notifications

### Notifications — `/api/notifications/`

list, unread-count, mark-all-read, `{id}/read`

### Courses — `/api/courses/` (upar)

### Enrollments — `/api/enrollments/`

GET list, POST `{ course_slug }`, GET `{course_slug}`

### Assessments — `/api/assessments/`

list, featured-quiz, `{id}`, `{id}/submit`, my-attempts

### Certificates — `/api/certificates/`

list, `{id}`, my-certificates, verify/{code}

### Legal — `/api/legal/{doc_type}/`, POST `/api/legal/accept/`

### Feedback — POST `/api/feedback/` (auth)

### Contact — `/api/contact/`

screen, message, messages (admin), questions

### About — `/api/about-us/`

screen, overview, stats, offers, stories, team  
Staff POST/PATCH detail routes for CMS.

### Issues — POST `/api/issues/report/` (user), GET `/api/issues/` (admin)

### Schema

- `GET /api/schema/`
- `GET /api/docs/` (Swagger; `drf-spectacular` INSTALLED_APPS me add karna pad sakta hai)

---

## Play API contract (backend must not break)

`GET /api/courses/content/{id}/play/`

**401** no token  
**403** not enrolled  
**200**

```json
{
  "content_id": 1,
  "lesson_id": 1,
  "course_id": 1,
  "course_slug": "python-for-beginners",
  "content_type": "VIDEO",
  "title": "Welcome Video",
  "url": "https://....mp4",
  "play_url": "https://....mp4",
  "mime_type": "video/mp4",
  "duration_seconds": 596,
  "duration_display": "9:56"
}
```

CORS Android native me zaroori nahi. Agar WebView use ho to CORS alag se add karna.

---

## Tests

```bash
python manage.py test courses
```
