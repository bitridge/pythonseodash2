from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    CustomUser, Client, Project, SEOLog, ReportSection, 
    Media, UserSettings, SEOLogFile, Notification
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'last_login')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'website_link', 'logo_preview', 'project_count', 'created_at')
    search_fields = ('name', 'email', 'website')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at', 'logo_preview')
    
    def website_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website)
    website_link.short_description = 'Website'
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.logo.url)
        return '-'
    logo_preview.short_description = 'Logo'
    
    def project_count(self, obj):
        count = obj.project_set.count()
        url = reverse('admin:core_project_changelist') + f'?client__id__exact={obj.id}'
        return format_html('<a href="{}">{} projects</a>', url, count)
    project_count.short_description = 'Projects'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client_link', 'start_date', 'end_date', 'status', 'seo_log_count')
    search_fields = ('name', 'client__name', 'description')
    list_filter = ('start_date', 'end_date', 'client')
    readonly_fields = ('created_at', 'updated_at')
    
    def client_link(self, obj):
        url = reverse('admin:core_client_change', args=[obj.client.id])
        return format_html('<a href="{}">{}</a>', url, obj.client.name)
    client_link.short_description = 'Client'
    
    def status(self, obj):
        if not obj.end_date:
            return format_html('<span style="color: green;">Active</span>')
        return format_html('<span style="color: red;">Completed</span>')
    
    def seo_log_count(self, obj):
        count = obj.seolog_set.count()
        url = reverse('admin:core_seolog_changelist') + f'?project__id__exact={obj.id}'
        return format_html('<a href="{}">{} logs</a>', url, count)
    seo_log_count.short_description = 'SEO Logs'

@admin.register(SEOLog)
class SEOLogAdmin(admin.ModelAdmin):
    list_display = ('project_link', 'date', 'created_by', 'work_type', 'file_count')
    list_filter = ('date', 'created_by', 'project', 'on_page_work', 'off_page_work')
    search_fields = ('project__name', 'created_by__username', 'on_page_description', 'off_page_description')
    readonly_fields = ('created_by',)
    filter_horizontal = ('providers',)
    
    def project_link(self, obj):
        url = reverse('admin:core_project_change', args=[obj.project.id])
        return format_html('<a href="{}">{}</a>', url, obj.project.name)
    project_link.short_description = 'Project'
    
    def work_type(self, obj):
        types = []
        if obj.on_page_work:
            types.append('On-Page')
        if obj.off_page_work:
            types.append('Off-Page')
        return ', '.join(types) or '-'
    work_type.short_description = 'Work Type'
    
    def file_count(self, obj):
        count = obj.files.count()
        if count:
            url = reverse('admin:core_seologfile_changelist') + f'?seo_log__id__exact={obj.id}'
            return format_html('<a href="{}">{} files</a>', url, count)
        return '0 files'
    file_count.short_description = 'Files'

@admin.register(ReportSection)
class ReportSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'order', 'image_preview')
    search_fields = ('title', 'project__name', 'content')
    list_filter = ('project', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    ordering = ('project', 'order')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Image'

@admin.register(SEOLogFile)
class SEOLogFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'seo_log_link', 'work_type', 'file_size_formatted', 'uploaded_at')
    list_filter = ('work_type', 'uploaded_at', 'file_type')
    search_fields = ('file_name', 'seo_log__project__name')
    readonly_fields = ('file_size', 'file_type', 'uploaded_at')
    
    def seo_log_link(self, obj):
        url = reverse('admin:core_seolog_change', args=[obj.seo_log.id])
        return format_html('<a href="{}">{} - {}</a>', url, obj.seo_log.project.name, obj.seo_log.date)
    seo_log_link.short_description = 'SEO Log'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    readonly_fields = ('created_at',)

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'date_format', 'notify_new_project')
    list_filter = ('theme', 'notify_new_project', 'notify_new_log', 'notify_report')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
