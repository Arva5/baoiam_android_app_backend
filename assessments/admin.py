from django.contrib import admin
from .models import Assessment, Option, Question, UserAssessmentAttempt


class OptionInline(admin.TabularInline):
    model = Option
    extra = 3


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'quiz_type', 'estimated_minutes', 'badge_text', 'is_featured', 'is_active')
    list_filter = ('is_active', 'is_featured', 'quiz_type')
    search_fields = ('title', 'subtitle', 'description')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'assessment', 'question_text', 'order', 'is_active')
    list_filter = ('assessment', 'is_active')
    search_fields = ('question_text',)
    inlines = [OptionInline]


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'option_text', 'career_track', 'order')
    search_fields = ('option_text', 'career_track')


@admin.register(UserAssessmentAttempt)
class UserAssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'assessment', 'recommended_path', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'completed_at', 'assessment')
    search_fields = ('user__email', 'assessment__title', 'recommended_path')
