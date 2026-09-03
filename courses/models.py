from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    icon_url = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Course(models.Model):
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all_levels', 'All Levels'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    short_code = models.CharField(
        max_length=10, blank=True,
        help_text="Short badge text shown in the app, e.g. 'UI/UX', 'WD', 'DA', 'PM'."
    )
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    cover_image_url = models.URLField(max_length=500, blank=True, null=True)

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="courses_taught",
        help_text="Left nullable for now — a dedicated Instructor role/model can replace this later.",
    )
    instructor_name = models.CharField(max_length=150, default='Baoiam Instructor', blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='all_levels')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.8)
    reviews_count = models.PositiveIntegerField(default=0)
    duration_hours = models.DecimalField(max_digits=5, decimal_places=1, default=10.0)
    lessons_count = models.PositiveIntegerField(default=12)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    discounted_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def total_lectures(self):
        """Matches lecture count, falling back to lessons_count if modules aren't yet populated."""
        count = Lesson.objects.filter(module__course=self).count()
        return count if count > 0 else self.lessons_count


class CourseModule(models.Model):
    """A module/section within a course (e.g. 'Module 2: Ideation & Wireframing')."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0, help_text="Display order within the course (Module 1, 2, 3...).")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("course", "order")

    def __str__(self):
        return f"{self.course.title} - Module {self.order}: {self.title}"


class Lesson(models.Model):
    """
    A single lecture within a module (e.g. 'Lecture 2: Wireframing Basics').
    One lesson can hold multiple ContentItems (its recording, its PDF notes, etc.).
    """

    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0, help_text="Lecture number within the module (Lecture 1, 2, 3...).")
    published_at = models.DateField(
        null=True, blank=True,
        help_text="Date shown in the app, e.g. '12 May 2025'."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("module", "order")

    def __str__(self):
        return f"{self.module} - Lecture {self.order}: {self.title}"

    @property
    def course(self):
        return self.module.course


class ContentItem(models.Model):
    """
    A single piece of content attached to a lesson.
    """

    class ContentType(models.TextChoices):
        VIDEO = "VIDEO", "Video Recording"
        PDF = "PDF", "PDF"
        ARTICLE = "ARTICLE", "Article"
        EXTERNAL_LINK = "EXTERNAL_LINK", "External Link"
        QUIZ = "QUIZ", "Quiz"
        ASSIGNMENT = "ASSIGNMENT", "Assignment"
        PROJECT = "PROJECT", "Project"
        LIVE_CLASS = "LIVE_CLASS", "Live Class"

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="content_items")
    content_type = models.CharField(max_length=20, choices=ContentType.choices)
    title = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    duration_seconds = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="For VIDEO items — used to show '45:20' style durations in the app."
    )
    file_size_bytes = models.PositiveBigIntegerField(
        null=True, blank=True,
        help_text="For PDF/file items — used to show '2.4 MB' style sizes in the app."
    )
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"[{self.content_type}] {self.title}"

    @property
    def duration_display(self):
        if self.duration_seconds is None:
            return None
        minutes, seconds = divmod(self.duration_seconds, 60)
        return f"{minutes}:{seconds:02d}"


class CourseEnrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course_enrollments'
    )
    progress_percentage = models.PositiveIntegerField(default=0)
    completed_lessons = models.PositiveIntegerField(default=0)
    total_lessons = models.PositiveIntegerField(default=0)
    current_lesson_title = models.CharField(max_length=255, blank=True)
    is_completed = models.BooleanField(default=False)
    last_accessed_at = models.DateTimeField(auto_now=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-last_accessed_at']

    def __str__(self):
        return f"{self.user} - {self.course.title} ({self.progress_percentage}%)"


class PromotionalBanner(models.Model):
    TARGET_TYPE_CHOICES = (
        ('course', 'Course'),
        ('category', 'Category'),
        ('quiz', 'Learning Path Quiz'),
        ('external', 'External Link'),
        ('custom', 'Custom Action'),
    )

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    tagline = models.CharField(max_length=255, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    badge_text = models.CharField(max_length=50, blank=True, default='SPECIAL OFFER')
    discount_code = models.CharField(max_length=50, blank=True)
    discount_percentage = models.PositiveIntegerField(default=0)
    target_type = models.CharField(max_length=30, choices=TARGET_TYPE_CHOICES, default='course')
    target_id = models.CharField(max_length=100, blank=True)
    target_url = models.URLField(max_length=500, blank=True, null=True)
    button_text = models.CharField(max_length=50, default='Claim Offer')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def is_currently_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


class TipOfTheDay(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=100, default='Learning Strategy')
    author_name = models.CharField(max_length=150, default='Baoiam Mentor')
    author_avatar_url = models.URLField(max_length=500, blank=True, null=True)
    icon_name = models.CharField(max_length=50, blank=True, default='lightbulb')
    publish_date = models.DateField(default=timezone.now, null=True, blank=True, db_index=True)
    likes_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tip of the Day'
        verbose_name_plural = 'Tips of the Day'
        ordering = ['-publish_date', '-created_at']

    def __str__(self):
        return self.title


class WhyChooseUsItem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon_url = models.URLField(max_length=500, blank=True, null=True)
    icon_name = models.CharField(max_length=50, blank=True, default='star')
    highlight_stat = models.CharField(max_length=50, blank=True, help_text="e.g. '98% Success Rate'")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Why Choose Us Item'
        verbose_name_plural = 'Why Choose Us Items'
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title
