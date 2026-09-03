from django.contrib import admin

from .models import (
    Category,
    ContentItem,
    Course,
    CourseEnrollment,
    CourseModule,
    Lesson,
    PromotionalBanner,
    TipOfTheDay,
    WhyChooseUsItem,
)


class ContentItemInline(admin.TabularInline):
    model = ContentItem
    extra = 1


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'short_code',
        'category',
        'instructor',
        'level',
        'price',
        'rating',
        'is_featured',
        'is_popular',
        'is_published',
        'created_at',
    )
    list_filter = ('is_published', 'is_featured', 'is_popular', 'level', 'category')
    search_fields = ('title', 'short_code', 'subtitle', 'instructor_name')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CourseModuleInline]


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'order', 'title')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'module', 'order', 'title', 'published_at')
    list_filter = ('module__course',)
    search_fields = ('title', 'module__title')
    inlines = [ContentItemInline]


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content_type', 'lesson', 'duration_display', 'order')
    list_filter = ('content_type',)
    search_fields = ('title', 'lesson__title')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'course',
        'progress_percentage',
        'completed_lessons',
        'is_completed',
        'last_accessed_at',
    )
    list_filter = ('is_completed', 'enrolled_at')
    search_fields = ('user__email', 'course__title')


@admin.register(PromotionalBanner)
class PromotionalBannerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'badge_text',
        'discount_code',
        'discount_percentage',
        'target_type',
        'order',
        'is_active',
        'start_date',
        'end_date',
    )
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'target_type')
    search_fields = ('title', 'subtitle', 'discount_code')


@admin.register(TipOfTheDay)
class TipOfTheDayAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'author_name', 'publish_date', 'likes_count', 'is_active')
    list_filter = ('is_active', 'category', 'publish_date')
    search_fields = ('title', 'content', 'author_name')


@admin.register(WhyChooseUsItem)
class WhyChooseUsItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'highlight_stat', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description', 'highlight_stat')
