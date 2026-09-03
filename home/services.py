from django.utils import timezone
from accounts.models import UserProfile
from assessments.models import Assessment, UserAssessmentAttempt
from certificates.models import Certificate, UserCertificate
from courses.models import (
    Course,
    CourseEnrollment,
    PromotionalBanner,
    TipOfTheDay,
    WhyChooseUsItem,
)


def get_getting_started_data(user):
    """
    Computes backend-driven user onboarding status.
    Checks:
      1. Profile completion
      2. Course exploration / enrollment
      3. Learning start status
    """
    is_authenticated = bool(user and user.is_authenticated)

    profile_done = False
    enrollment_done = False
    learning_done = False

    if is_authenticated:
        # Check profile completion
        profile = getattr(user, 'profile', None)
        if profile and (profile.is_profile_completed or profile.headline or profile.skills or profile.interests):
            profile_done = True
        elif user.name and user.email_verified:
            profile_done = True

        # Check course enrollment
        enrollments_qs = CourseEnrollment.objects.filter(user=user)
        enrollment_done = enrollments_qs.exists()

        # Check learning start status (any progress made or lesson completed)
        learning_done = (
            enrollments_qs.filter(completed_lessons__gt=0).exists()
            or enrollments_qs.filter(progress_percentage__gt=0).exists()
        )


    completed_count = sum([1 for x in [profile_done, enrollment_done, learning_done] if x])
    progress_percentage = int(round((completed_count / 3.0) * 100))
    is_completed = (completed_count == 3)

    steps = [
        {
            "id": "profile_completion",
            "title": "Complete Your Profile",
            "description": "Set up your interests, role, and career goals to personalize your experience.",
            "is_completed": profile_done,
            "action_type": "navigate",
            "action_url": "baoiam://profile/edit",
        },
        {
            "id": "course_exploration",
            "title": "Enroll in Your First Course",
            "description": "Explore curated tracks and add your first course to your learning space.",
            "is_completed": enrollment_done,
            "action_type": "navigate",
            "action_url": "baoiam://courses",
        },
        {
            "id": "learning_start",
            "title": "Start Your First Lesson",
            "description": "Watch your first video lesson or complete your first interactive exercise.",
            "is_completed": learning_done,
            "action_type": "navigate",
            "action_url": "baoiam://learning/continue",
        },
    ]

    return {
        "title": "Getting Started",
        "subtitle": "Complete these quick steps to jumpstart your learning journey",
        "progress_percentage": progress_percentage,
        "completed_steps_count": completed_count,
        "total_steps_count": 3,
        "is_completed": is_completed,
        "steps": steps,
    }


def get_promotional_banners_data():
    """
    Returns active promotional offers and banners for Home Screen 1.
    """
    now = timezone.now()
    banners = PromotionalBanner.objects.filter(
        is_active=True
    ).exclude(
        start_date__gt=now
    ).exclude(
        end_date__lt=now
    ).order_by('order', '-created_at')

    results = []
    for b in banners:
        results.append({
            "id": b.id,
            "title": b.title,
            "subtitle": b.subtitle,
            "tagline": b.tagline,
            "image_url": b.image_url,
            "badge_text": b.badge_text,
            "discount_code": b.discount_code,
            "discount_percentage": b.discount_percentage,
            "target_type": b.target_type,
            "target_id": b.target_id,
            "target_url": b.target_url,
            "button_text": b.button_text,
            "start_date": b.start_date,
            "end_date": b.end_date,
        })
    return results


def get_learning_path_quiz_data(user):
    """
    Retrieves the featured Learning Path Quiz from assessments.
    """
    quiz = Assessment.objects.filter(
        is_active=True,
        is_featured=True
    ).prefetch_related('questions').first()

    if not quiz:
        quiz = Assessment.objects.filter(is_active=True).prefetch_related('questions').first()

    if not quiz:
        return {
            "is_available": False,
            "quiz": None,
            "user_status": None,
        }

    user_status = None
    if user and user.is_authenticated:
        attempt = UserAssessmentAttempt.objects.filter(
            user=user,
            assessment=quiz,
            is_completed=True
        ).order_by('-completed_at').first()
        if attempt:
            user_status = {
                "has_attempted": True,
                "attempt_id": attempt.id,
                "recommended_path": attempt.recommended_path,
                "completed_at": attempt.completed_at,
            }
        else:
            user_status = {
                "has_attempted": False,
                "attempt_id": None,
                "recommended_path": None,
                "completed_at": None,
            }
    else:
        user_status = {
            "has_attempted": False,
            "attempt_id": None,
            "recommended_path": None,
            "completed_at": None,
        }

    return {
        "is_available": True,
        "quiz": {
            "id": quiz.id,
            "title": quiz.title,
            "subtitle": quiz.subtitle or "Find the perfect learning track matched to your ambition",
            "description": quiz.description,
            "thumbnail_url": quiz.thumbnail_url,
            "quiz_type": quiz.quiz_type,
            "estimated_minutes": quiz.estimated_minutes,
            "questions_count": quiz.questions_count,
            "badge_text": quiz.badge_text,
        },
        "user_status": user_status,
    }


def get_why_choose_us_data():
    """
    Retrieves value propositions and features from WhyChooseUsItem.
    """
    items = WhyChooseUsItem.objects.filter(is_active=True).order_by('order')
    results = []
    for item in items:
        results.append({
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "icon_url": item.icon_url,
            "icon_name": item.icon_name,
            "highlight_stat": item.highlight_stat,
        })
    return {
        "title": "Why Choose Baoiam?",
        "subtitle": "Transform your career with world-class mentors and project-driven learning",
        "items": results,
    }


def get_tip_of_the_day_data():
    """
    Retrieves today's tip or latest active tip.
    """
    today = timezone.localdate()
    tip = TipOfTheDay.objects.filter(
        is_active=True,
        publish_date=today
    ).first()

    if not tip:
        tip = TipOfTheDay.objects.filter(is_active=True).first()

    if not tip:
        return None

    return {
        "id": tip.id,
        "title": tip.title,
        "content": tip.content,
        "category": tip.category,
        "author_name": tip.author_name,
        "author_avatar_url": tip.author_avatar_url,
        "icon_name": tip.icon_name,
        "publish_date": tip.publish_date,
        "likes_count": tip.likes_count,
    }


def get_start_your_journey_data(user):
    """
    Connects relevant user/course/certificate progress data.
    """
    is_authenticated = bool(user and user.is_authenticated)

    if is_authenticated:
        # User enrollments
        enrollments = CourseEnrollment.objects.filter(
            user=user
        ).select_related('course', 'course__category').order_by('-last_accessed_at')

        total_enrolled = enrollments.count()
        completed_courses = enrollments.filter(is_completed=True).count()
        in_progress_courses = enrollments.filter(is_completed=False)

        # Primary active course to resume
        primary_resume = None
        current_active = in_progress_courses.first() or enrollments.first()
        if current_active:
            primary_resume = {
                "enrollment_id": current_active.id,
                "course_id": current_active.course.id,
                "course_title": current_active.course.title,
                "course_thumbnail_url": current_active.course.thumbnail_url,
                "category_name": current_active.course.category.name if current_active.course.category else None,
                "progress_percentage": current_active.progress_percentage,
                "completed_lessons": current_active.completed_lessons,
                "total_lessons": current_active.total_lessons,
                "current_lesson_title": current_active.current_lesson_title or "Next Scheduled Lesson",
                "last_accessed_at": current_active.last_accessed_at,
            }

        # User certificates
        user_certs = UserCertificate.objects.filter(
            user=user,
            is_verified=True
        ).select_related('certificate')
        certificates_count = user_certs.count()
        latest_cert = user_certs.first()
        latest_certificate_info = None
        if latest_cert:
            latest_certificate_info = {
                "certificate_code": latest_cert.certificate_code,
                "title": latest_cert.certificate.title,
                "issued_at": latest_cert.issued_at,
                "badge_icon_url": latest_cert.certificate.badge_icon_url,
            }


        # Next milestone / goal
        if primary_resume:
            milestone_text = f"Complete {primary_resume['course_title']} ({primary_resume['progress_percentage']}% completed)"
        else:
            milestone_text = "Enroll in your next course to earn a certificate"

        return {
            "journey_state": "in_progress" if total_enrolled > 0 else "new_learner",
            "is_authenticated": True,
            "headline": f"Welcome back, {user.name}!" if user.name else "Welcome back!",
            "subheadline": "Pick up where you left off or explore new skills today.",
            "enrolled_courses_count": total_enrolled,
            "completed_courses_count": completed_courses,
            "certificates_earned_count": certificates_count,
            "primary_resume_course": primary_resume,
            "latest_certificate": latest_certificate_info,
            "next_milestone": milestone_text,
            "recommended_starter_course": None,
        }

    else:
        # Guest / unauthenticated user: recommend starter course & display platform milestones
        starter_course = Course.objects.filter(
            is_published=True,
            is_featured=True
        ).first() or Course.objects.filter(is_published=True).first()

        starter_info = None
        if starter_course:
            starter_info = {
                "course_id": starter_course.id,
                "title": starter_course.title,
                "subtitle": starter_course.subtitle,
                "thumbnail_url": starter_course.thumbnail_url,
                "level": starter_course.level,
                "duration_hours": starter_course.duration_hours,
                "rating": str(starter_course.rating),
            }

        return {
            "journey_state": "guest",
            "is_authenticated": False,
            "headline": "Start Your Learning Journey Today",
            "subheadline": "Join thousands of learners building real skills and high-growth careers.",
            "enrolled_courses_count": 0,
            "completed_courses_count": 0,
            "certificates_earned_count": 0,
            "primary_resume_course": None,
            "latest_certificate": None,
            "next_milestone": "Sign in to unlock personalized learning paths & certificates",
            "recommended_starter_course": starter_info,
        }


def get_home_screen_1_engagement(user):
    """
    Main aggregator for Home Screen 1: Engagement Content.
    Returns all 6 sections in one payload:
      1. Getting Started
      2. Promotional Banner
      3. Learning Path Quiz
      4. Why Choose Us
      5. Tip of the Day
      6. Start Your Journey
    """
    return {
        "getting_started": get_getting_started_data(user),
        "promotional_banners": get_promotional_banners_data(),
        "learning_path_quiz": get_learning_path_quiz_data(user),
        "why_choose_us": get_why_choose_us_data(),
        "tip_of_the_day": get_tip_of_the_day_data(),
        "start_your_journey": get_start_your_journey_data(user),
    }
