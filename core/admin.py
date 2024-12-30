from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Customer, Project, SEOLog,
    ReportSection, Media, UserSettings, SEOLogFile, Notification
)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'website', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'email', 'website')
    ordering = ('name',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date', 'customer')
    search_fields = ('name', 'description', 'customer__name')
    ordering = ('name',)

class SEOLogAdmin(admin.ModelAdmin):
    list_display = ('project', 'date', 'created_by', 'on_page_work', 'off_page_work')
    list_filter = ('date', 'on_page_work', 'off_page_work', 'project__customer')
    search_fields = ('project__name', 'project__customer__name', 'on_page_description', 'off_page_description')
    ordering = ('-date',)

class ReportSectionAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'order', 'created_at')
    list_filter = ('project__customer', 'created_at')
    search_fields = ('title', 'content', 'project__name', 'project__customer__name')
    ordering = ('project', 'order')

class MediaAdmin(admin.ModelAdmin):
    list_display = ('seo_log', 'file_type', 'created_at')
    list_filter = ('file_type', 'created_at', 'seo_log__project__customer')
    search_fields = ('description', 'seo_log__project__name', 'seo_log__project__customer__name')
    ordering = ('-created_at',)

class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'date_format', 'report_format')
    list_filter = ('theme', 'date_format', 'report_format')
    search_fields = ('user__username', 'user__email')

class SEOLogFileAdmin(admin.ModelAdmin):
    list_display = ('seo_log', 'file_name', 'file_type', 'work_type', 'uploaded_at')
    list_filter = ('work_type', 'file_type', 'uploaded_at', 'seo_log__project__customer')
    search_fields = ('file_name', 'seo_log__project__name', 'seo_log__project__customer__name')
    ordering = ('-uploaded_at',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'message')
    ordering = ('-created_at',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(SEOLog, SEOLogAdmin)
admin.site.register(ReportSection, ReportSectionAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(UserSettings, UserSettingsAdmin)
admin.site.register(SEOLogFile, SEOLogFileAdmin)
admin.site.register(Notification, NotificationAdmin)
