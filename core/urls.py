from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Dashboard URLs
    path('', views.dashboard, name='dashboard'),
    
    # Customer URLs
    path('customers/', views.customer_list, name='customers'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/toggle-status/', views.customer_toggle_status, name='customer_toggle_status'),
    
    # Project URLs
    path('projects/', views.project_list, name='projects'),
    path('projects/add/', views.project_add, name='project_add'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/toggle-status/', views.project_toggle_status, name='project_toggle_status'),
    
    # SEO Log URLs
    path('seo-logs/', views.seo_log_list, name='seo_logs'),
    path('seo-logs/add/', views.seo_log_add, name='seo_log_add'),
    path('seo-logs/<int:pk>/', views.seo_log_detail, name='seo_log_detail'),
    path('seo-logs/<int:pk>/edit/', views.seo_log_edit, name='seo_log_edit'),
    path('seo-logs/<int:pk>/delete/', views.seo_log_delete, name='seo_log_delete'),
    
    # Report URLs
    path('reports/', views.report_list, name='report_list'),
    path('reports/create/<int:project_pk>/', views.report_create, name='report_create'),
    path('reports/<int:pk>/', views.report_detail, name='report_detail'),
    path('reports/<int:pk>/edit/', views.report_edit, name='report_edit'),
    path('reports/<int:report_pk>/sections/add/', views.report_section_add, name='report_section_add'),
    path('reports/<int:pk>/download/', views.report_download, name='report_download'),
    path('attachments/<int:pk>/download/', views.attachment_download, name='attachment_download'),
    path('reports/<int:pk>/review/', views.report_review, name='report_review'),
    path('reports/<int:pk>/publish/', views.report_publish, name='report_publish'),
    path('reports/<int:pk>/delete/', views.report_delete, name='report_delete'),
    
    # Settings URLs
    path('settings/', views.settings_view, name='settings'),
    path('settings/notifications/', views.settings_notifications, name='settings_notifications'),
    path('settings/appearance/', views.settings_appearance, name='settings_appearance'),
    path('settings/reports/', views.settings_reports, name='settings_reports'),
    path('settings/integrations/', views.settings_integrations, name='settings_integrations'),
    path('settings/system/', views.settings_system, name='settings_system'),
] 