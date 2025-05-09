from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login as auth_login
from django.contrib.auth.models import User
from judge.func import is_valid_username, is_strong_password
from judge.models import Problem

def index(request):
    return render(request, 'index.html')

def problems(request):
    return render(request, 'problems.html', {
        'problems': Problem.objects.all().order_by('id')
    })

def problem(request, problem_id):
    return render(request, 'problem.html', {
        'problem': Problem.objects.get(id=problem_id)
    })

def submission_list(request):
    return render(request, 'submissions.html')

def signup(request):
    messages = []

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not is_valid_username(username):
            messages.append({"type": "warning", "text": "Tên tài khoản phải từ 5–15 ký tự, chỉ gồm chữ và số."})
        elif password1 != password2:
            messages.append({"type": "warning", "text": "Mật khẩu không khớp."})
        elif not is_strong_password(password1):
            messages.append({"type": "warning", "text": "Mật khẩu phải từ 8–32 ký tự, gồm chữ, số và ký tự đặc biệt."})
        elif User.objects.filter(username=username).exists():
            messages.append({"type": "danger", "text": "Tên đăng nhập đã tồn tại."})
        elif User.objects.filter(email=email).exists():
            messages.append({"type": "danger", "text": "Email đã được sử dụng."})
        else:
            User.objects.create_user(username=username, email=email, password=password1)
            messages.append({"type": "success", "text": "Tạo tài khoản thành công!"})

    return render(request, 'signup.html', {'messages': messages})

def login(request):
    messages = []

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')  # hoặc chuyển hướng đến trang bạn muốn
        else:
            messages.append({"type": "danger", "text": "Tên đăng nhập hoặc mật khẩu không đúng."})

    return render(request, 'login.html', {'messages': messages})

def custom_logout(request):
    logout(request)
    return redirect('index')