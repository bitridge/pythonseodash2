from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Customer, Project, SEOLog,
    ReportSection, Media, UserSettings, SEOLogFile, Notification,
    Report, ReportAttachment, ReportSectionOrder, ReportVersion, AttachmentAccess
)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff', 'is_active'),
        }),
    )

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
    list_display = ('project', 'date', 'created_by', 'work_type')
    list_filter = ('date', 'work_type', 'project__customer')
    search_fields = ('project__name', 'project__customer__name', 'description')
    ordering = ('-date',)

class ReportSectionAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'priority', 'created_at')
    list_filter = ('project__customer', 'created_at')
    search_fields = ('title', 'content', 'project__name', 'project__customer__name')
    ordering = ('project', 'priority')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'created_by', 'created_at', 'status', 'version']
    list_filter = ['status', 'created_at', 'project']
    search_fields = ['title', 'description', 'project__name']
    date_hierarchy = 'created_at'

class ReportVersionAdmin(admin.ModelAdmin):
    list_display = ('report', 'version_number', 'created_by', 'created_at')
    list_filter = ('created_at', 'report__project__customer')
    search_fields = ('report__title', 'changes', 'report__project__name')
    ordering = ('-created_at',)

class ReportAttachmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_section', 'file_type', 'file_size', 'created_at')
    list_filter = ('file_type', 'created_at', 'report_section__project__customer')
    search_fields = ('title', 'description', 'report_section__title')
    ordering = ('-created_at',)

class AttachmentAccessAdmin(admin.ModelAdmin):
    list_display = ('attachment', 'user', 'accessed_at', 'ip_address')
    list_filter = ('accessed_at', 'attachment__report_section__project__customer')
    search_fields = ('user__email', 'attachment__title', 'ip_address')
    ordering = ('-accessed_at',)

class ReportSectionOrderAdmin(admin.ModelAdmin):
    list_display = ('report', 'section', 'order', 'page_break_before')
    list_filter = ('page_break_before', 'report__project__customer')
    search_fields = ('report__title', 'section__title')
    ordering = ('report', 'order')

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
    list_filter = ('file_type', 'work_type', 'uploaded_at', 'seo_log__project__customer')
    search_fields = ('file_name', 'seo_log__project__name', 'seo_log__project__customer__name')
    ordering = ('-uploaded_at',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    ordering = ('-created_at',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(SEOLog, SEOLogAdmin)
admin.site.register(ReportSection, ReportSectionAdmin)
admin.site.register(ReportVersion, ReportVersionAdmin)
admin.site.register(ReportAttachment, ReportAttachmentAdmin)
admin.site.register(AttachmentAccess, AttachmentAccessAdmin)
admin.site.register(ReportSectionOrder, ReportSectionOrderAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(UserSettings, UserSettingsAdmin)
admin.site.register(SEOLogFile, SEOLogFileAdmin)
admin.site.register(Notification, NotificationAdmin)
