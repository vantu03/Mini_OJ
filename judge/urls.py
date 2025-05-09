from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('problems/', views.problems, name='problems'),
    path('problem/<int:problem_id>/', views.problem, name='problem'),
    path('problem/<int:problem_id>/submit/', views.submit, name='submit'),
    path('submissions/', views.submission_list, name='submission_list'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
]
