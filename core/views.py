from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse
from functools import wraps
from .models import Client, Project, SEOLog, ReportSection, Media, UserSettings, CustomUser, SEOLogFile
from .forms import (
    CustomUserForm, ClientForm, ProjectForm, SEOLogForm,
    ReportSectionForm, MediaForm
)
from django.template.loader import render_to_string, get_template
from django.utils import timezone
from django.conf import settings
from weasyprint import HTML

def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in roles:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

@login_required
def dashboard(request):
    context = {
        'title': 'Dashboard',
    }
    
    # Get recent logs (last 30 days)
    thirty_days_ago = timezone.now().date() - timezone.timedelta(days=30)
    
    if request.user.role == 'admin':
        context.update({
            'total_clients': Client.objects.count(),
            'total_projects': Project.objects.filter(end_date__isnull=True).count(),
            'recent_logs': SEOLog.objects.filter(date__gte=thirty_days_ago).order_by('-date')[:10],
            'reports_count': ReportSection.objects.values('project').distinct().count(),
            'active_users': CustomUser.objects.filter(last_login__date=timezone.now().date()).count(),
            'storage_used': get_storage_used(),
            'last_backup': get_last_backup_date(),
        })
    elif request.user.role == 'provider':
        context.update({
            'assigned_projects': Project.objects.filter(
                providers=request.user,
                is_active=True,
                client__is_active=True
            ),
            'recent_logs': SEOLog.objects.filter(
                created_by=request.user,
                date__gte=thirty_days_ago,
                project__is_active=True,
                project__client__is_active=True
            ).order_by('-date')[:10],
            'reports_count': ReportSection.objects.filter(
                project__providers=request.user,
                project__is_active=True,
                project__client__is_active=True
            ).values('project').distinct().count(),
        })
    else:  # client
        context.update({
            'client_projects': Project.objects.filter(
                client__email=request.user.email,
                is_active=True,
                client__is_active=True
            ),
            'recent_logs': SEOLog.objects.filter(
                project__client__email=request.user.email,
                date__gte=thirty_days_ago,
                project__is_active=True,
                project__client__is_active=True
            ).order_by('-date')[:10],
            'reports_count': ReportSection.objects.filter(
                project__client__email=request.user.email,
                project__is_active=True,
                project__client__is_active=True
            ).values('project').distinct().count(),
        })
    
    return render(request, 'core/dashboard.html', context)

def get_storage_used():
    """Calculate total storage used by media files"""
    from django.conf import settings
    import os
    
    total_size = 0
    media_root = settings.MEDIA_ROOT
    
    for dirpath, dirnames, filenames in os.walk(media_root):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    
    # Convert to MB
    return f"{total_size / (1024 * 1024):.1f} MB"

def get_last_backup_date():
    """Get the date of the last backup"""
    # This is a placeholder. Implement actual backup date retrieval based on your backup system
    return None

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = CustomUserForm(instance=request.user, user=request.user)
    
    return render(request, 'core/profile.html', {
        'title': 'Profile Settings',
        'form': form
    })

@login_required
@role_required(['admin', 'provider'])
def client_list(request):
    clients = Client.objects.all().order_by('name')
    return render(request, 'core/client_list.html', {
        'title': 'Clients',
        'clients': clients,
    })

@login_required
@role_required(['admin', 'provider'])
def client_add(request):
    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES)
        if form.is_valid():
            client = form.save()
            messages.success(request, 'Client added successfully.')
            return redirect('client_detail', pk=client.pk)
    else:
        form = ClientForm()
    
    return render(request, 'core/client_form.html', {
        'title': 'Add Client',
        'form': form,
    })

@login_required
def project_list(request):
    if request.user.role == 'admin':
        projects = Project.objects.all()
    elif request.user.role == 'provider':
        projects = Project.objects.filter(
            providers=request.user,
            is_active=True,
            client__is_active=True
        )
    else:  # client
        projects = Project.objects.filter(
            client__email=request.user.email,
            is_active=True,
            client__is_active=True
        )
    
    return render(request, 'core/project_list.html', {
        'title': 'Projects',
        'projects': projects,
    })

@login_required
@role_required(['admin', 'provider'])
def project_add(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, 'Project added successfully.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'core/project_form.html', {
        'title': 'Add Project',
        'form': form,
    })

@login_required
@role_required(['admin', 'provider'])
def seo_log_list(request):
    # Get base queryset based on user role
    if request.user.role == 'provider':
        logs = SEOLog.objects.filter(created_by=request.user)
        projects = Project.objects.filter(seolog__created_by=request.user).distinct()
    else:
        logs = SEOLog.objects.all()
        projects = Project.objects.all()
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        logs = logs.filter(description__icontains=search)
    
    project_id = request.GET.get('project')
    if project_id:
        logs = logs.filter(project_id=project_id)
    
    log_type = request.GET.get('type')
    if log_type == 'on_page':
        logs = logs.filter(on_page_work=True)
    elif log_type == 'off_page':
        logs = logs.filter(off_page_work=True)
    
    date_range = request.GET.get('date')
    if date_range == 'today':
        logs = logs.filter(date=timezone.now().date())
    elif date_range == 'week':
        week_ago = timezone.now().date() - timezone.timedelta(days=7)
        logs = logs.filter(date__gte=week_ago)
    elif date_range == 'month':
        month_ago = timezone.now().date() - timezone.timedelta(days=30)
        logs = logs.filter(date__gte=month_ago)
    
    # Order by most recent
    logs = logs.order_by('-date')
    
    return render(request, 'core/seo_log_list.html', {
        'title': 'SEO Logs',
        'logs': logs,
        'projects': projects,
    })

@login_required
@role_required(['admin', 'provider'])
def seo_log_add(request):
    if request.method == 'POST':
        form = SEOLogForm(request.user, request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.created_by = request.user
            log.save()
            messages.success(request, 'SEO log added successfully.')
            return redirect('seo_log_detail', pk=log.pk)
    else:
        form = SEOLogForm(request.user)
    
    return render(request, 'core/seo_log_form.html', {
        'title': 'Add SEO Log',
        'form': form,
    })

@login_required
def report_list(request):
    if request.user.role == 'client':
        projects = Project.objects.filter(client__email=request.user.email)
    elif request.user.role == 'provider':
        projects = Project.objects.filter(seolog__created_by=request.user).distinct()
    else:  # admin
        projects = Project.objects.all()
    
    return render(request, 'core/report_list.html', {
        'title': 'Reports',
        'projects': projects,
    })

@login_required
def report_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user.role == 'client' and project.client.email != request.user.email:
        return HttpResponseForbidden("You don't have permission to access this report.")
    
    report_sections = ReportSection.objects.filter(project=project).order_by('order')
    return render(request, 'core/report_detail.html', {
        'title': f'Report: {project.name}',
        'project': project,
        'report_sections': report_sections,
    })

@login_required
def report_generate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        selected_logs = request.POST.getlist('selected_logs')
        selected_files = request.POST.getlist('selected_files')
        section_titles = request.POST.getlist('section_titles[]')
        section_contents = request.POST.getlist('section_contents[]')
        
        # Get selected logs and files
        seo_logs = SEOLog.objects.filter(id__in=selected_logs).order_by('date')
        files = SEOLogFile.objects.filter(id__in=selected_files)
        
        # Prepare custom sections
        custom_sections = []
        for title, content in zip(section_titles, section_contents):
            if title and content:  # Only add if both title and content are provided
                custom_sections.append({
                    'title': title,
                    'content': content
                })
        
        # Generate PDF report
        context = {
            'project': project,
            'seo_logs': seo_logs,
            'files': files,
            'custom_sections': custom_sections,
            'generated_date': timezone.now()
        }
        
        # Render PDF template
        template = get_template('core/report_pdf.html')
        html = template.render(context)
        
        # Create PDF
        pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
        
        # Create response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{project.name}_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
        return response
    
    # GET request - show form
    context = {
        'project': project,
        'seo_logs': SEOLog.objects.filter(project=project).order_by('-date'),
        'files': SEOLogFile.objects.filter(seo_log__project=project)
    }
    return render(request, 'core/report_generate_form.html', context)

@login_required
@role_required(['admin', 'provider'])
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    projects = Project.objects.filter(client=client)
    return render(request, 'core/client_detail.html', {
        'title': f'Client: {client.name}',
        'client': client,
        'projects': projects,
    })

@login_required
@role_required(['admin', 'provider'])
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client updated successfully.')
            return redirect('client_detail', pk=pk)
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'core/client_form.html', {
        'title': f'Edit Client: {client.name}',
        'form': form,
        'client': client,
    })

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user.role == 'client' and project.client.email != request.user.email:
        return HttpResponseForbidden("You don't have permission to access this project.")
    
    seo_logs = SEOLog.objects.filter(project=project).order_by('-date')
    return render(request, 'core/project_detail.html', {
        'title': f'Project: {project.name}',
        'project': project,
        'seo_logs': seo_logs,
    })

@login_required
@role_required(['admin', 'provider'])
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('project_detail', pk=pk)
    else:
        form = ProjectForm(instance=project, user=request.user)
    
    return render(request, 'core/project_form.html', {
        'title': f'Edit Project: {project.name}',
        'form': form,
        'project': project,
    })

@login_required
@role_required(['admin', 'provider'])
def seo_log_detail(request, pk):
    log = get_object_or_404(SEOLog, pk=pk)
    if request.user.role == 'provider' and log.created_by != request.user:
        return HttpResponseForbidden("You don't have permission to access this log.")
    
    return render(request, 'core/seo_log_detail.html', {
        'title': f'SEO Log: {log.project.name} - {log.date}',
        'log': log,
    })

@login_required
@role_required(['admin', 'provider'])
def seo_log_edit(request, pk):
    log = get_object_or_404(SEOLog, pk=pk)
    if request.user.role == 'provider' and log.created_by != request.user:
        return HttpResponseForbidden("You don't have permission to edit this log.")
    
    if request.method == 'POST':
        form = SEOLogForm(request.user, request.POST, instance=log)
        if form.is_valid():
            form.save()
            messages.success(request, 'SEO log updated successfully.')
            return redirect('seo_log_detail', pk=pk)
    else:
        form = SEOLogForm(request.user, instance=log)
    
    return render(request, 'core/seo_log_form.html', {
        'title': f'Edit SEO Log: {log.project.name} - {log.date}',
        'form': form,
        'log': log,
    })

@login_required
def settings_view(request):
    """Main settings view that shows all settings categories."""
    try:
        settings = request.user.settings
    except UserSettings.DoesNotExist:
        settings = UserSettings.objects.create(user=request.user)
    
    return render(request, 'core/settings.html', {
        'title': 'Settings',
        'settings': settings,
    })

@login_required
def settings_notifications(request):
    """Handle notification settings."""
    settings = request.user.settings
    if request.method == 'POST':
        settings.notify_new_project = request.POST.get('notify_new_project') == 'on'
        settings.notify_new_log = request.POST.get('notify_new_log') == 'on'
        settings.notify_report = request.POST.get('notify_report') == 'on'
        settings.save()
        messages.success(request, 'Notification settings updated successfully.')
        return redirect('settings_notifications')
    
    return render(request, 'core/settings_notifications.html', {
        'title': 'Notification Settings',
        'settings': settings,
    })

@login_required
def settings_appearance(request):
    """Handle appearance settings."""
    settings = request.user.settings
    if request.method == 'POST':
        settings.theme = request.POST.get('theme', 'light')
        settings.date_format = request.POST.get('date_format', 'YYYY-MM-DD')
        settings.save()
        messages.success(request, 'Appearance settings updated successfully.')
        return redirect('settings_appearance')
    
    return render(request, 'core/settings_appearance.html', {
        'title': 'Appearance Settings',
        'settings': settings,
    })

@login_required
def settings_reports(request):
    """Handle report settings."""
    settings = request.user.settings
    if request.method == 'POST':
        if request.FILES.get('report_logo'):
            settings.report_logo = request.FILES['report_logo']
        settings.report_format = request.POST.get('report_format', 'pdf')
        settings.save()
        messages.success(request, 'Report settings updated successfully.')
        return redirect('settings_reports')
    
    return render(request, 'core/settings_reports.html', {
        'title': 'Report Settings',
        'settings': settings,
    })

@login_required
def settings_integrations(request):
    """Handle integration settings."""
    settings = request.user.settings
    if request.method == 'POST':
        settings.ga_tracking_id = request.POST.get('ga_tracking_id', '')
        settings.gsc_verification = request.POST.get('gsc_verification', '')
        settings.save()
        messages.success(request, 'Integration settings updated successfully.')
        return redirect('settings_integrations')
    
    return render(request, 'core/settings_integrations.html', {
        'title': 'Integration Settings',
        'settings': settings,
    })

@login_required
@role_required(['admin'])
def settings_system(request):
    """Handle system settings (admin only)."""
    settings = request.user.settings
    if request.method == 'POST':
        settings.smtp_host = request.POST.get('smtp_host', '')
        settings.smtp_port = request.POST.get('smtp_port')
        settings.smtp_security = request.POST.get('smtp_security', 'tls')
        settings.auto_backup = request.POST.get('auto_backup') == 'on'
        settings.backup_frequency = request.POST.get('backup_frequency', 'weekly')
        settings.save()
        messages.success(request, 'System settings updated successfully.')
        return redirect('settings_system')
    
    return render(request, 'core/settings_system.html', {
        'title': 'System Settings',
        'settings': settings,
    })

@login_required
@role_required(['admin'])
def seo_log_delete(request, pk):
    log = get_object_or_404(SEOLog, pk=pk)
    project_id = log.project.id
    log.delete()
    messages.success(request, 'SEO log deleted successfully.')
    return redirect('project_detail', pk=project_id)

@login_required
@role_required(['admin'])
def report_delete(request, pk):
    report = get_object_or_404(ReportSection, pk=pk)
    project_id = report.project.id
    report.delete()
    messages.success(request, 'Report section deleted successfully.')
    return redirect('report_detail', pk=project_id)

@login_required
def report_section_add(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        seo_logs = request.POST.getlist('seo_logs')
        files = request.POST.getlist('files')
        
        section = ReportSection.objects.create(
            project=project,
            title=title,
            content=content,
            image=image,
            order=ReportSection.objects.filter(project=project).count() + 1
        )
        
        if seo_logs:
            section.seo_logs.set(seo_logs)
        if files:
            section.files.set(files)
        
        messages.success(request, 'Report section added successfully.')
        return redirect('report_detail', pk=pk)
    
    return redirect('report_detail', pk=pk)

@login_required
@role_required(['admin'])
def client_toggle_status(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.is_active = not client.is_active
    client.save()
    
    # When deactivating a client, deactivate all their projects
    if not client.is_active:
        client.project_set.all().update(is_active=False)
    
    status = 'activated' if client.is_active else 'deactivated'
    messages.success(request, f'Client {status} successfully.')
    return redirect('client_detail', pk=pk)

@login_required
@role_required(['admin'])
def project_toggle_status(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.is_active = not project.is_active
    project.save()
    status = 'activated' if project.is_active else 'deactivated'
    messages.success(request, f'Project {status} successfully.')
    return redirect('project_detail', pk=pk)
