from django.contrib import admin

from .models import ContentItem, Course, CourseModule, Lesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


class ContentItemInline(admin.TabularInline):
    model = ContentItem
    extra = 1


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "short_code", "instructor", "is_published", "total_lectures", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title", "short_code")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CourseModuleInline]


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ("course", "order", "title")
    list_filter = ("course",)
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("module", "order", "title", "published_at")
    list_filter = ("module__course",)
    inlines = [ContentItemInline]


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ("title", "content_type", "lesson", "duration_display", "order")
    list_filter = ("content_type",)
