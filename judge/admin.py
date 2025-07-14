from django.contrib import admin
from .models import Problem, TestCase, Submission, Language, SubmissionResult

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    class TestCaseInline(admin.StackedInline):
        model = TestCase
        extra = 1
        show_change_link = True

    list_display = ('title', 'time_limit', 'memory_limit')
    search_fields = ('title',)
    inlines = [TestCaseInline]

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'is_sample', 'score')
    list_filter = ('problem', 'is_sample')
    search_fields = ('problem__title',)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'language', 'status', 'submitted_at')
    list_filter = ('status', 'language', 'problem')
    search_fields = ('user__username', 'problem__title')

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('code', 'mode', 'name')
    search_fields = ('code', 'name')

@admin.register(SubmissionResult)
class SubmissionResultAdmin(admin.ModelAdmin):
    list_display = ('submission', 'test_case', 'status', 'execution_time', 'memory_used')
    list_filter = ('status', 'test_case__problem')
    search_fields = ('submission__user__username', 'test_case__problem__title')
