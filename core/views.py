from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse
from functools import wraps
from .models import Customer, Project, SEOLog, ReportSection, Media, UserSettings, CustomUser, SEOLogFile, Notification, Report, ReportVersion, ReportSectionOrder, ReportAttachment, AttachmentAccess
from .forms import (
    CustomUserForm, CustomerForm, ProjectForm, SEOLogForm,
    ReportSectionForm, MediaForm, ReportForm, RegisterForm, LoginForm
)
from django.template.loader import render_to_string, get_template
from django.utils import timezone
from django.conf import settings
from weasyprint import HTML
from django.contrib.auth import login, logout, authenticate
from django.utils.html import strip_tags

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
    today = timezone.now().date()
    user = request.user

    # Get counts based on user role
    if user.role == 'admin':
        customer_count = Customer.objects.count()
        active_projects_count = Project.objects.filter(is_active=True).count()
        todays_logs_count = SEOLog.objects.filter(date=today).count()
        reports_count = Report.objects.count()
        
        # Get active projects with progress
        active_projects = Project.objects.filter(is_active=True)[:5]
        for project in active_projects:
            total_logs = SEOLog.objects.filter(project=project).count()
            if total_logs > 0:
                completed_logs = SEOLog.objects.filter(
                    project=project, 
                    work_type__in=['completed', 'published']
                ).count()
                project.progress = int((completed_logs / total_logs) * 100)
            else:
                project.progress = 0
    
    elif user.role == 'provider':
        customer_count = Customer.objects.filter(projects__providers=user).distinct().count()
        active_projects_count = Project.objects.filter(providers=user, is_active=True).count()
        todays_logs_count = SEOLog.objects.filter(created_by=user, date=today).count()
        reports_count = Report.objects.filter(created_by=user).count()
        
        # Get provider's active projects with progress
        active_projects = Project.objects.filter(providers=user, is_active=True)[:5]
        for project in active_projects:
            total_logs = SEOLog.objects.filter(project=project, created_by=user).count()
            if total_logs > 0:
                completed_logs = SEOLog.objects.filter(
                    project=project,
                    created_by=user,
                    work_type__in=['completed', 'published']
                ).count()
                project.progress = int((completed_logs / total_logs) * 100)
            else:
                project.progress = 0
    
    else:  # customer
        try:
            customer = Customer.objects.get(email=user.email)
            customer_count = 1  # themselves
            active_projects_count = Project.objects.filter(customer=customer, is_active=True).count()
            todays_logs_count = SEOLog.objects.filter(project__customer=customer, date=today).count()
            reports_count = Report.objects.filter(project__customer=customer).count()
            
            # Get customer's active projects with progress
            active_projects = Project.objects.filter(customer=customer, is_active=True)[:5]
            for project in active_projects:
                total_logs = SEOLog.objects.filter(project=project).count()
                if total_logs > 0:
                    completed_logs = SEOLog.objects.filter(
                        project=project,
                        work_type__in=['completed', 'published']
                    ).count()
                    project.progress = int((completed_logs / total_logs) * 100)
                else:
                    project.progress = 0
        except Customer.DoesNotExist:
            messages.error(request, "No customer profile found for your account. Please contact an administrator.")
            customer_count = 0
            active_projects_count = 0
            todays_logs_count = 0
            reports_count = 0
            active_projects = []

    # Get recent activities
    recent_activities = []
    
    # Get recent SEO logs
    recent_logs = SEOLog.objects.select_related('project', 'created_by')
    if user.role == 'provider':
        recent_logs = recent_logs.filter(created_by=user)
    elif user.role == 'customer':
        try:
            customer = Customer.objects.get(email=user.email)
            recent_logs = recent_logs.filter(project__customer=customer)
        except Customer.DoesNotExist:
            recent_logs = SEOLog.objects.none()
    recent_logs = recent_logs.order_by('-date')[:5]
    
    for log in recent_logs:
        # Convert date to datetime for consistent comparison
        timestamp = timezone.datetime.combine(log.date, timezone.datetime.min.time())
        timestamp = timezone.make_aware(timestamp)
        # Strip HTML tags from description for clean display
        description = strip_tags(log.description)
        recent_activities.append({
            'type': 'log',
            'icon': 'fas fa-tasks',
            'color': 'success',
            'title': f'New SEO Log - {log.project.name}',
            'description': f'{log.get_work_type_display()}: {description[:100]}...',
            'timestamp': timestamp
        })
    
    # Get recent reports
    recent_reports = Report.objects.select_related('project', 'created_by')
    if user.role == 'provider':
        recent_reports = recent_reports.filter(created_by=user)
    elif user.role == 'customer':
        try:
            customer = Customer.objects.get(email=user.email)
            recent_reports = recent_reports.filter(project__customer=customer)
        except Customer.DoesNotExist:
            recent_reports = Report.objects.none()
    recent_reports = recent_reports.order_by('-created_at')[:5]
    
    for report in recent_reports:
        recent_activities.append({
            'type': 'report',
            'icon': 'fas fa-file-alt',
            'color': 'primary',
            'title': f'New Report - {report.project.name}',
            'description': report.title,
            'timestamp': report.created_at
        })
    
    # Sort activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:10]  # Limit to 10 most recent activities

    context = {
        'customer_count': customer_count,
        'active_projects_count': active_projects_count,
        'todays_logs_count': todays_logs_count,
        'reports_count': reports_count,
        'active_projects': active_projects,
        'recent_activities': recent_activities,
    }

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
def customer_list(request):
    customers = Customer.objects.all().order_by('name')
    return render(request, 'core/customer_list.html', {
        'title': 'Customers',
        'customers': customers,
    })

@login_required
@role_required(['admin', 'provider'])
def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            customer = form.save()
            messages.success(request, 'Customer added successfully.')
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    
    return render(request, 'core/customer_form.html', {
        'title': 'Add Customer',
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
            customer__is_active=True
        )
    else:  # customer
        projects = Project.objects.filter(
            customer__email=request.user.email,
            is_active=True,
            customer__is_active=True
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
        providers = [request.user]  # Only show current provider
    else:
        logs = SEOLog.objects.all()
        projects = Project.objects.all()
        providers = CustomUser.objects.filter(role='provider')  # Get all providers
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        logs = logs.filter(description__icontains=search)
    
    project_id = request.GET.get('project')
    if project_id:
        logs = logs.filter(project_id=project_id)
    
    log_type = request.GET.get('type')
    if log_type:
        logs = logs.filter(work_type=log_type)
    
    provider_id = request.GET.get('provider')
    if provider_id and request.user.role == 'admin':  # Only admin can filter by provider
        logs = logs.filter(created_by_id=provider_id)
    
    date_range = request.GET.get('date')
    if date_range == 'today':
        logs = logs.filter(date=timezone.now().date())
    elif date_range == 'week':
        week_ago = timezone.now().date() - timezone.timedelta(days=7)
        logs = logs.filter(date__gte=week_ago)
    elif date_range == 'month':
        month_ago = timezone.now().date() - timezone.timedelta(days=30)
        logs = logs.filter(date__gte=month_ago)
    
    # Order by most recent and select related fields for optimization
    logs = logs.select_related('project', 'created_by').order_by('-date')
    
    return render(request, 'core/seo_log_list.html', {
        'title': 'SEO Logs',
        'logs': logs,
        'projects': projects,
        'providers': providers,
        'log_types': SEOLog.WORK_TYPE_CHOICES,
    })

@login_required
@role_required(['admin', 'provider'])
def seo_log_add(request):
    if request.method == 'POST':
        form = SEOLogForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            seo_log = form.save(commit=False)
            seo_log.created_by = request.user
            seo_log.date = timezone.now().date()
            seo_log.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Handle file uploads
            files = request.FILES.getlist('files')
            for file in files:
                # Get file extension
                ext = file.name.split('.')[-1].lower()
                # Determine file type based on extension
                if ext in ['jpg', 'jpeg', 'png', 'gif']:
                    file_type = 'image'
                elif ext in ['pdf', 'doc', 'docx']:
                    file_type = 'document'
                elif ext in ['xls', 'xlsx']:
                    file_type = 'spreadsheet'
                else:
                    file_type = 'other'
                
                SEOLogFile.objects.create(
                    seo_log=seo_log,
                    file=file,
                    work_type=seo_log.work_type,
                    file_name=file.name,
                    file_type=file_type,
                    file_size=file.size
                )
            
            messages.success(request, 'SEO Log added successfully!')
            return redirect('seo_logs')
    else:
        form = SEOLogForm(user=request.user)
    
    return render(request, 'core/seo_log_form.html', {
        'title': 'Add SEO Log',
        'form': form,
    })

@login_required
def report_list(request):
    if request.user.role == 'admin':
        reports = Report.objects.all()
    elif request.user.role == 'provider':
        reports = Report.objects.filter(project__providers=request.user)
    else:  # customer
        reports = Report.objects.filter(project__customer__email=request.user.email)
    
    reports = reports.order_by('-created_at')
    
    return render(request, 'core/report_list.html', {
        'title': 'Reports',
        'reports': reports,
    })

@login_required
@role_required(['admin', 'provider'])
def report_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    
    # Check if user has permission to create report for this project
    if request.user.role == 'provider' and request.user not in project.providers.all():
        return HttpResponseForbidden("You don't have permission to create reports for this project.")
    
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES, project=project, user=request.user)
        if form.is_valid():
            try:
                # Create the report
                report = form.save(commit=False)
                report.project = project
                report.created_by = request.user
                report.save()
                
                # Get all section data
                section_titles = request.POST.getlist('section_title[]')
                section_priorities = request.POST.getlist('section_priority[]')
                section_contents = request.POST.getlist('section_content[]')
                section_files = request.FILES.getlist('section_attachments[]')
                
                # Create sections
                for i, title in enumerate(section_titles):
                    # Create the report section
                    section = ReportSection.objects.create(
                        project=project,
                        title=title,
                        content=section_contents[i],
                        priority=int(section_priorities[i])
                    )
                    
                    # Add selected work logs
                    selected_logs = form.cleaned_data.get('selected_logs', [])
                    if selected_logs:
                        section.seo_logs.set(selected_logs)
                    
                    # Handle attachments for this section
                    if i < len(section_files):
                        file = section_files[i]
                        attachment = ReportAttachment.objects.create(
                            report_section=section,
                            file=file,
                            title=file.name,
                            file_type=file.content_type,
                            file_size=file.size
                        )
                    
                    # Add section to report with proper order
                    ReportSectionOrder.objects.create(
                        report=report,
                        section=section,
                        order=int(section_priorities[i]),
                        page_break_before=True
                    )
                
                # Create initial version
                ReportVersion.objects.create(
                    report=report,
                    version_number=1,
                    created_by=request.user,
                    changes='Initial version'
                )
                
                messages.success(request, 'Report created successfully.')
                return redirect('report_detail', pk=report.pk)
            except Exception as e:
                messages.error(request, f'Error creating report: {str(e)}')
                return redirect('report_create', project_pk=project_pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReportForm(project=project, user=request.user)
    
    return render(request, 'core/report_form.html', {
        'title': 'Create Report',
        'form': form,
        'project': project,
    })

@login_required
def report_detail(request, pk):
    report = get_object_or_404(Report, pk=pk)
    
    # Check permissions
    if request.user.role == 'customer' and report.project.customer.email != request.user.email:
        return HttpResponseForbidden()
    elif request.user.role == 'provider' and request.user not in report.project.providers.all():
        return HttpResponseForbidden()
    
    sections = report.sections.all().order_by('reportsectionorder__order')
    versions = report.versions.all()
    
    context = {
        'title': report.title,
        'report': report,
        'sections': sections,
        'versions': versions,
        'can_edit': report.can_edit(request.user),
        'can_review': report.can_review(request.user),
        'can_publish': report.can_publish(request.user),
        'is_admin': request.user.role == 'admin'
    }
    
    return render(request, 'core/report_detail.html', context)

@login_required
@role_required(['admin', 'provider'])
def report_edit(request, pk):
    report = get_object_or_404(Report, pk=pk)
    
    if request.method == 'POST':
        form = ReportForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save()
            
            # Create new version
            version = ReportVersion.objects.create(
                report=report,
                version_number=report.version + 1,
                created_by=request.user,
                changes=request.POST.get('changes', '')
            )
            
            report.version = version.version_number
            report.save()
            
            messages.success(request, 'Report updated successfully.')
            return redirect('report_detail', pk=report.pk)
    else:
        form = ReportForm(instance=report)
    
    sections = report.sections.all().order_by('reportsectionorder__order')
    
    return render(request, 'core/report_edit.html', {
        'title': f'Edit Report: {report.title}',
        'form': form,
        'report': report,
        'sections': sections,
    })

@login_required
@role_required(['admin', 'provider'])
def report_section_add(request, report_pk):
    report = get_object_or_404(Report, pk=report_pk)
    
    if request.method == 'POST':
        form = ReportSectionForm(request.POST, request.FILES)
        if form.is_valid():
            section = form.save(commit=False)
            section.project = report.project
            section.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Add to report with next order number
            next_order = ReportSectionOrder.objects.filter(report=report).count() + 1
            ReportSectionOrder.objects.create(
                report=report,
                section=section,
                order=next_order
            )
            
            messages.success(request, 'Section added successfully.')
            return redirect('report_edit', pk=report.pk)
    else:
        form = ReportSectionForm()
        # Filter SEO logs based on project
        form.fields['seo_logs'].queryset = SEOLog.objects.filter(project=report.project)
    
    return render(request, 'core/report_section_form.html', {
        'title': 'Add Section',
        'form': form,
        'report': report,
    })

@login_required
def report_download(request, pk):
    report = get_object_or_404(Report, pk=pk)
    
    # Check permissions
    if request.user.role == 'customer' and report.project.customer.email != request.user.email:
        return HttpResponseForbidden()
    elif request.user.role == 'provider' and request.user not in report.project.providers.all():
        return HttpResponseForbidden()
    
    # Generate PDF
    template = get_template('core/report_pdf.html')
    sections = report.sections.all().order_by('reportsectionorder__order')
    
    context = {
        'report': report,
        'sections': sections,
        'base_url': request.build_absolute_uri('/')[:-1],
    }
    
    html = template.render(context)
    pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    
    # Create response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report.title}.pdf"'
    return response

@login_required
def attachment_download(request, pk):
    attachment = get_object_or_404(ReportAttachment, pk=pk)
    
    # Check permissions
    report = attachment.report_section.project.report_set.first()
    if request.user.role == 'customer' and report.project.customer.email != request.user.email:
        return HttpResponseForbidden()
    elif request.user.role == 'provider' and request.user not in report.project.providers.all():
        return HttpResponseForbidden()
    
    # Log access
    AttachmentAccess.objects.create(
        attachment=attachment,
        user=request.user,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Stream file
    response = HttpResponse(attachment.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{attachment.file.name}"'
    return response

@login_required
@role_required(['admin', 'provider'])
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    projects = Project.objects.filter(customer=customer)
    return render(request, 'core/customer_detail.html', {
        'title': f'Customer: {customer.name}',
        'customer': customer,
        'projects': projects,
    })

@login_required
@role_required(['admin', 'provider'])
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully.')
            return redirect('customer_detail', pk=pk)
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'core/customer_form.html', {
        'title': f'Edit Customer: {customer.name}',
        'form': form,
        'customer': customer,
    })

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user.role == 'customer' and project.customer.email != request.user.email:
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
        form = SEOLogForm(request.POST, request.FILES, user=request.user, instance=log)
        if form.is_valid():
            log = form.save(commit=False)
            log.save()
            form.save_m2m()  # Save many-to-many relationships and files
            messages.success(request, 'SEO log updated successfully.')
            return redirect('seo_log_detail', pk=pk)
    else:
        form = SEOLogForm(instance=log, user=request.user)
    
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
        settings.keep_as_draft = request.POST.get('keep_as_draft') == 'on'
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
@role_required(['admin'])
def customer_toggle_status(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.is_active = not customer.is_active
    customer.save()
    
    # When deactivating a customer, deactivate all their projects
    if not customer.is_active:
        customer.project_set.all().update(is_active=False)
    
    status = 'activated' if customer.is_active else 'deactivated'
    messages.success(request, f'Customer {status} successfully.')
    return redirect('customer_detail', pk=pk)

@login_required
@role_required(['admin'])
def project_toggle_status(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.is_active = not project.is_active
    project.save()
    status = 'activated' if project.is_active else 'deactivated'
    messages.success(request, f'Project {status} successfully.')
    return redirect('project_detail', pk=pk)

@login_required
@role_required(['admin'])
def report_review(request, pk):
    report = get_object_or_404(Report, pk=pk)
    
    if request.method == 'POST' and report.can_review(request.user):
        decision = request.POST.get('decision')
        notes = request.POST.get('review_notes', '')
        
        if decision == 'approve':
            report.mark_as_reviewed(request.user, notes)
            messages.success(request, 'Report has been approved.')
        else:
            report.status = 'draft'
            report.review_notes = notes
            report.save()
            messages.info(request, 'Report has been sent back for revision.')
            
    return redirect('report_detail', pk=pk)

@login_required
@role_required(['admin'])
def report_publish(request, pk):
    report = get_object_or_404(Report, pk=pk)
    
    if request.method == 'POST' and report.can_publish(request.user):
        report.publish()
        messages.success(request, 'Report has been published successfully.')
    
    return redirect('report_detail', pk=pk)

@login_required
@role_required(['admin'])
def report_delete(request, pk):
    report = get_object_or_404(Report, pk=pk)
    project_id = report.project.id
    
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Report deleted successfully.')
        return redirect('project_detail', pk=project_id)
    
    return redirect('report_detail', pk=pk)

def home(request):
    return render(request, 'core/home.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'core/auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'core/auth/register.html', {'form': form})

@login_required
@role_required(['admin'])
def user_list(request):
    users = CustomUser.objects.all().order_by('username')
    return render(request, 'core/user_list.html', {
        'title': 'User Management',
        'users': users,
    })

@login_required
@role_required(['admin'])
def user_add(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Set a default password if not provided
            password = form.cleaned_data.get('password', None)
            if password:
                user.set_password(password)
            else:
                user.set_password('changeme123')  # Default password
            user.save()
            messages.success(request, 'User added successfully. Default password is "changeme123" if none was provided.')
            return redirect('user_list')
    else:
        form = CustomUserForm()
    
    return render(request, 'core/user_form.html', {
        'title': 'Add User',
        'form': form,
    })

@login_required
@role_required(['admin'])
def user_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('user_list')
    else:
        form = CustomUserForm(instance=user)
    
    return render(request, 'core/user_form.html', {
        'title': f'Edit User: {user.username}',
        'form': form,
        'user_obj': user,
    })

@login_required
@role_required(['admin'])
def user_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('user_list')
    return redirect('user_list')
