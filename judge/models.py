from django.db import models
from django.contrib.auth.models import User

#Ngôn ngữ lập trình
class Language(models.Model):
    code = models.CharField(max_length=10, unique=True)
    mode = models.CharField(max_length=30)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"

# Bài toán lập trình
class Problem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(255)
    content = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()
    time_limit = models.FloatField(default=1.0, help_text="Second")
    memory_limit = models.IntegerField(default=256, help_text="MB")
    languages = models.ManyToManyField(Language)

    def __str__(self):
        return self.title

# Test case chấm tự động
class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)
    score = models.FloatField(default=1.0)

# Lần nộp bài
class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices= [
            ('PENDING', 'Pending'),
            ('SUBMITTED', 'Submitted'),
            ('COMPILE_ERROR', 'Compilation Error'),
            ('SYSTEM_ERROR', 'System Error'),
        ], default='PENDING')

class SubmissionResult(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    actual_output = models.TextField(blank=True)
    expected_output = models.TextField(blank=True)
    execution_time = models.FloatField(null=True, blank=True, help_text="Second")
    memory_used = models.FloatField(null=True, blank=True, help_text="MB")
    message = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('ACCEPTED', 'Accepted'),
            ('WRONG_ANSWER', 'Wrong Answer'),
            ('TLE', 'Time Limit Exceeded'),
            ('MLE', 'Memory Limit Exceeded'),
            ('RUNTIME_ERROR', 'Runtime Error'),
            ('COMPILE_ERROR', 'Compilation Error'),
            ('SYSTEM_ERROR', 'System Error'),
        ],
        default='PENDING'
    )
