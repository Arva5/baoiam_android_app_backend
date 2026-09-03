from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Course(models.Model):
    """
    A single course a student can enroll in.
    (Program, the level above Course in the blueprint, can be added later
    as its own model with a FK from Course once multi-course bundles are needed.)
    """

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    short_code = models.CharField(
        max_length=10, blank=True,
        help_text="Short badge text shown in the app, e.g. 'UI/UX', 'WD', 'DA', 'PM'."
    )
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(blank=True)

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="courses_taught",
        help_text="Left nullable for now — a dedicated Instructor role/model can replace this later.",
    )

    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def total_lectures(self):
        """Matches the 'Total Lectures: 24' count shown on the Recordings screen."""
        return Lesson.objects.filter(module__course=self).count()


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
    One lesson can hold multiple ContentItems (its recording, its PDF notes,
    an assignment, etc.) — matching the blueprint's Course Player design
    where a lesson shows a video plus a Resources list.
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
    A single piece of content attached to a lesson. `content_type` decides
    which screen it surfaces in: VIDEO -> Recordings tab, PDF/ARTICLE/
    EXTERNAL_LINK -> Materials tab. QUIZ/ASSIGNMENT/PROJECT/LIVE_CLASS are
    included now so later phases (Assessment/Assignment/Project/Live Class
    engines) can hang off this same content model instead of a new one.
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

    # Generic enough to hold a video URL, a PDF/file URL, or an external link.
    # Actual video storage/streaming provider (S3/Cloudinary/etc.) is a
    # separate infra decision — this field just stores whatever URL results.
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
        """Formats duration_seconds as 'MM:SS' to match the design (e.g. '45:20')."""
        if self.duration_seconds is None:
            return None
        minutes, seconds = divmod(self.duration_seconds, 60)
        return f"{minutes}:{seconds:02d}"
