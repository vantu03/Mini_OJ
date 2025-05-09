from django.db import models
from django.contrib.auth.models import User

#Ngôn ngữ lập trình
class Language(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)

# Bài toán lập trình
class Problem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()
    time_limit = models.FloatField(default=2.0)  # Giây
    memory_limit = models.IntegerField(default=256)  # MB
    languages = models.ManyToManyField(Language)

# Test case chấm tự động
class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)
    score = models.FloatField(default=1.0)

# Các trạng thái sau khi chấm bài
VERDICT_CHOICES = [
    ('PENDING', 'Pending'),
    ('ACCEPTED', 'Accepted'),
    ('WRONG_ANSWER', 'Wrong Answer'),
    ('TLE', 'Time Limit Exceeded'),
    ('MLE', 'Memory Limit Exceeded'),
    ('RUNTIME_ERROR', 'Runtime Error'),
    ('COMPILE_ERROR', 'Compilation Error'),
    ('SYSTEM_ERROR', 'System Error'),
]

# Lần nộp bài
class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    verdict = models.CharField(max_length=20, choices=VERDICT_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, null=True)
