from django.urls import path
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView,
    PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index/", views.index, name="index"),
    path("upload/", views.upload_resume, name="upload_resume"),
    path("ats-checker/", views.ats_checker_view, name="ats_checker"),
    path("chat/", views.chat_view, name="chat"),
    path("api/ats_checker/", views.ats_checker_api, name="ats_checker_api"),
    path("api/chat/", views.chat_api, name="chat_api"),

    # Auth paths
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    # Password reset
    path('password_reset/', PasswordResetView.as_view(template_name='extractor/password_reset.html'), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='extractor/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='extractor/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='extractor/password_reset_complete.html'), name='password_reset_complete'),

    # Profile
    path('profile/', views.profile_view, name='profile'),

    # Upskilling System (Free AI-based)
    path('upskilling/', views.upskilling_view, name='upskilling'),
    path('api/upskilling/analyze/', views.upskilling_analyze_api, name='upskilling_analyze_api'),
    path('api/upskilling/job-roles/', views.upskilling_job_roles_api, name='upskilling_job_roles_api'),
    path('upskilling/history/', views.upskilling_history_view, name='upskilling_history'),

    # Redirects for old HTML routes
    path('ats_checker.html', RedirectView.as_view(url='/ats-checker/', permanent=True)),
    path('chat.html', RedirectView.as_view(url='/chat/', permanent=True)),
    path('login.html', RedirectView.as_view(url='/login/', permanent=True)),
    path('signup.html', RedirectView.as_view(url='/signup/', permanent=True)),

    # Optional favicon redirect
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
]
