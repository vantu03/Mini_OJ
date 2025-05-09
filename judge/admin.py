from django.contrib import admin
from .models import Problem, TestCase, Submission, Language

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'time_limit', 'memory_limit')

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'is_sample', 'score')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'problem', 'language', 'verdict', 'submitted_at')
    list_filter = ('verdict', 'language', 'problem')

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('code', 'mode', 'name')
