from django.contrib import admin
from .models import Problem, TestCase, Submission, Language, SubmissionResult

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    class TestCaseInline(admin.StackedInline):
        model = TestCase
        extra = 1
        show_change_link = True  # nếu muốn có link chỉnh sửa riêng

    list_display = ('title', 'time_limit', 'memory_limit')
    inlines = [TestCaseInline]

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'is_sample', 'score')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'language', 'verdict', 'submitted_at')
    list_filter = ('verdict', 'language', 'problem')

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('code', 'mode', 'name')

@admin.register(SubmissionResult)
class SubmissionResultAdmin(admin.ModelAdmin):
    list_display = ('submission', 'test_case', 'passed', 'execution_time')