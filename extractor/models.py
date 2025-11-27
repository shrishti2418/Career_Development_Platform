from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.user.username


class Resume(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    file = models.FileField(upload_to='resumes/')
    skills = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    projects = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    github_links = models.TextField(blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

# login/signup models can use Django's built-in User model
class signup(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    confirm_password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



# custom login model
class login(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Upskilling Analysis Model
class UpskillingAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    resume_file = models.FileField(upload_to='upskilling_resumes/', blank=True)
    target_job_role = models.CharField(max_length=200)
    skills_detected = models.TextField(blank=True)  # JSON string of detected skills
    skills_required = models.TextField(blank=True)  # JSON string of required skills
    skill_gaps = models.TextField(blank=True)  # JSON string of missing skills
    recommended_courses = models.TextField(blank=True)  # JSON string of course recommendations
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.target_job_role} - {self.created_at.strftime('%Y-%m-%d')}"