from django.contrib import admin
from .models import Resume, UserProfile, UpskillingAnalysis

# Register your models here.
@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'user', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['name', 'email', 'skills']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'name']
    search_fields = ['user__username', 'name']

@admin.register(UpskillingAnalysis)
class UpskillingAnalysisAdmin(admin.ModelAdmin):
    list_display = ['target_job_role', 'user', 'created_at']
    list_filter = ['created_at', 'target_job_role']
    search_fields = ['target_job_role', 'user__username']
    readonly_fields = ['created_at']
