from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Client, Project, SEOLog, ReportSection, Media

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'website', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'start_date', 'end_date')
    search_fields = ('name', 'client__name')
    list_filter = ('start_date', 'end_date', 'client')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SEOLog)
class SEOLogAdmin(admin.ModelAdmin):
    list_display = ('project', 'date', 'created_by', 'created_at')
    search_fields = ('project__name', 'created_by__username')
    list_filter = ('date', 'created_by', 'project')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ReportSection)
class ReportSectionAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'order')
    search_fields = ('project__name', 'title')
    list_filter = ('project',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('project', 'order')

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('seo_log', 'file_type', 'created_at')
    search_fields = ('seo_log__project__name', 'file_type')
    list_filter = ('file_type', 'created_at')
    readonly_fields = ('created_at',)
