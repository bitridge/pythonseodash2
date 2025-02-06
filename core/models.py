from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
import bleach
import os
from .utils import generate_unique_filename

# Define CustomUser before Project
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('provider', 'Provider'),
        ('customer', 'Customer'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return self.username

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    website = models.URLField()
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField(max_length=255, blank=True, help_text="Project website URL")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    providers = models.ManyToManyField(CustomUser, related_name='assigned_projects', blank=True, limit_choices_to={'role': 'provider'})

    def __str__(self):
        return f"{self.customer.name} - {self.name}"

class SEOLog(models.Model):
    WORK_TYPE_CHOICES = [
        ('on_page', 'On-Page SEO'),
        ('off_page', 'Off-Page SEO'),
        ('technical', 'Technical SEO'),
        ('content', 'Content Optimization'),
        ('analytics', 'Analytics & Tracking'),
        ('other', 'Other'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_logs')
    work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES, default='other')
    description = models.TextField(default='', blank=True)
    providers = models.ManyToManyField(CustomUser, related_name='assigned_logs', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.project.name} - {self.get_work_type_display()} - {self.date}"

    class Meta:
        ordering = ['-date']
        verbose_name = 'SEO Log'
        verbose_name_plural = 'SEO Logs'

    def save(self, *args, **kwargs):
        if self.description:
            # Define allowed tags and attributes
            allowed_tags = [
                'p', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'strong', 'em', 'u',
                'span', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'br'
            ]
            allowed_attrs = {
                '*': ['class'],
                'span': ['style'],
                'p': ['style'],
                'td': ['colspan', 'rowspan'],
                'th': ['colspan', 'rowspan']
            }
            
            # Clean the HTML content using bleach
            cleaned_html = bleach.clean(
                self.description,
                tags=allowed_tags,
                attributes=allowed_attrs,
                strip=True
            )
            
            # Linkify URLs in the content
            self.description = bleach.linkify(cleaned_html)
            
        super().save(*args, **kwargs)

class SEOLogFile(models.Model):
    WORK_TYPE_CHOICES = [
        ('on_page', 'On-Page'),
        ('off_page', 'Off-Page'),
    ]

    seo_log = models.ForeignKey(SEOLog, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='')  # Store in main media folder
    work_type = models.CharField(max_length=10, choices=WORK_TYPE_CHOICES)
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_size = models.IntegerField()  # Size in bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            if self.file:
                # Generate unique filename with seo prefix
                original_filename = self.file.name
                new_filename = generate_unique_filename(original_filename, prefix='seo')
                
                # Set the new filename
                self.file.name = new_filename
                
                # Set file name
                self.file_name = new_filename
                
                # Get file type from extension
                ext = os.path.splitext(self.file.name)[1].lower()[1:]  # Remove the dot
                if ext in ['jpg', 'jpeg', 'png', 'gif']:
                    self.file_type = f'image/{ext}'
                elif ext == 'pdf':
                    self.file_type = 'application/pdf'
                elif ext in ['doc', 'docx']:
                    self.file_type = 'application/msword'
                elif ext in ['xls', 'xlsx']:
                    self.file_type = 'application/vnd.ms-excel'
                else:
                    self.file_type = 'application/octet-stream'
                
                # Set file size
                self.file_size = self.file.size
                
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'SEO Log File'
        verbose_name_plural = 'SEO Log Files'

    @property
    def file_size_formatted(self):
        """Return human-readable file size."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @property
    def is_image(self):
        """Check if the file is an image."""
        return self.file_type.startswith('image/')

    @property
    def file_icon(self):
        """Return Font Awesome icon class based on file type."""
        if self.file_type.startswith('image/'):
            return 'fas fa-file-image'
        elif self.file_type == 'application/pdf':
            return 'fas fa-file-pdf'
        elif 'spreadsheet' in self.file_type or 'excel' in self.file_type:
            return 'fas fa-file-excel'
        elif 'document' in self.file_type or 'word' in self.file_type:
            return 'fas fa-file-word'
        elif 'presentation' in self.file_type or 'powerpoint' in self.file_type:
            return 'fas fa-file-powerpoint'
        elif 'zip' in self.file_type or 'rar' in self.file_type:
            return 'fas fa-file-archive'
        else:
            return 'fas fa-file'

class ReportSection(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.PositiveIntegerField(default=1, help_text="Priority determines page order (1 starts on first page)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    files = models.ManyToManyField('SEOLogFile', blank=True)
    seo_logs = models.ManyToManyField('SEOLog', blank=True)

    class Meta:
        ordering = ['priority', 'created_at']

    def __str__(self):
        return f"{self.project.name} - {self.title}"

class ReportAttachment(models.Model):
    report_section = models.ForeignKey(ReportSection, on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='')  # Store in main media folder
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField()  # Size in bytes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            if self.file:
                # Generate unique filename with report prefix
                original_filename = self.file.name
                new_filename = generate_unique_filename(original_filename, prefix='report')
                
                # Set the new filename
                self.file.name = new_filename
                
                # Set title if not provided
                if not self.title:
                    self.title = os.path.splitext(original_filename)[0]
                
                # Get file type from extension
                ext = os.path.splitext(self.file.name)[1].lower()[1:]  # Remove the dot
                if ext in ['jpg', 'jpeg', 'png', 'gif']:
                    self.file_type = 'image'
                elif ext == 'pdf':
                    self.file_type = 'pdf'
                elif ext in ['doc', 'docx']:
                    self.file_type = 'document'
                elif ext in ['xls', 'xlsx']:
                    self.file_type = 'spreadsheet'
                else:
                    self.file_type = 'other'
                
                # Set file size
                self.file_size = self.file.size
        
        super().save(*args, **kwargs)

    @property
    def file_size_formatted(self):
        """Return human-readable file size."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

class Report(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sections = models.ManyToManyField(ReportSection, through='ReportSectionOrder')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_template = models.BooleanField(default=False)
    publish_date = models.DateField(null=True, blank=True)
    last_reviewed_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_reports'
    )
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.project.name}"

    class Meta:
        ordering = ['-created_at']
        
    def get_absolute_url(self):
        return reverse('report_detail', kwargs={'pk': self.pk})

    def can_edit(self, user):
        return (
            user.role == 'admin' or 
            (user.role == 'provider' and self.status == 'draft' and user == self.created_by)
        )

    def can_review(self, user):
        return user.role == 'admin' and self.status == 'in_review'

    def can_publish(self, user):
        return user.role == 'admin' and self.status == 'approved'

    def mark_as_reviewed(self, user, notes=''):
        self.last_reviewed_by = user
        self.last_reviewed_at = timezone.now()
        self.review_notes = notes
        self.status = 'approved'
        self.save()

    def publish(self):
        if self.status == 'approved':
            self.status = 'published'
            self.publish_date = timezone.now().date()
            self.save()

class ReportSectionOrder(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    section = models.ForeignKey(ReportSection, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    page_break_before = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        unique_together = ['report', 'order']

class ReportVersion(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    created_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    changes = models.TextField()
    pdf_file = models.FileField(upload_to='report_versions/%Y/%m/', null=True, blank=True)

    class Meta:
        ordering = ['-version_number']
        unique_together = ['report', 'version_number']

    def __str__(self):
        return f"{self.report.title} - v{self.version_number}"

class AttachmentAccess(models.Model):
    attachment = models.ForeignKey(ReportAttachment, on_delete=models.CASCADE)
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    accessed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-accessed_at']

    def __str__(self):
        return f"{self.attachment.title} - {self.user.email} - {self.accessed_at}"

class Media(models.Model):
    seo_log = models.ForeignKey(SEOLog, on_delete=models.CASCADE)
    file = models.FileField(upload_to='media/')
    file_type = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seo_log.project.name} - {self.file_type}"

class UserSettings(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='settings')
    
    # Notification Settings
    notify_new_project = models.BooleanField(default=True)
    notify_new_log = models.BooleanField(default=True)
    notify_report = models.BooleanField(default=True)
    
    # Appearance Settings
    theme = models.CharField(max_length=10, default='light', choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'System Default'),
    ])
    date_format = models.CharField(max_length=20, default='YYYY-MM-DD', choices=[
        ('MM/DD/YYYY', 'MM/DD/YYYY'),
        ('DD/MM/YYYY', 'DD/MM/YYYY'),
        ('YYYY-MM-DD', 'YYYY-MM-DD'),
    ])
    
    # Report Settings
    report_format = models.CharField(max_length=10, default='pdf', choices=[
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ])
    report_logo = models.ImageField(upload_to='report_logos/', null=True, blank=True)
    keep_as_draft = models.BooleanField(default=True, help_text="Keep new reports as draft by default")
    
    # Integration Settings
    ga_tracking_id = models.CharField(max_length=50, blank=True)
    gsc_verification = models.CharField(max_length=100, blank=True)
    
    # System Settings (Admin Only)
    smtp_host = models.CharField(max_length=100, blank=True)
    smtp_port = models.IntegerField(null=True, blank=True)
    smtp_security = models.CharField(max_length=10, default='tls', choices=[
        ('tls', 'TLS'),
        ('ssl', 'SSL'),
        ('none', 'None'),
    ])
    auto_backup = models.BooleanField(default=False)
    backup_frequency = models.CharField(max_length=10, default='weekly', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Settings for {self.user.username}"

    class Meta:
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('project_assigned', 'Project Assigned'),
        ('seo_log_added', 'SEO Log Added'),
        ('report_generated', 'Report Generated'),
        ('project_completed', 'Project Completed'),
        ('comment_added', 'Comment Added'),
        ('file_uploaded', 'File Uploaded'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    @classmethod
    def create_notification(cls, user, type, title, message, link=''):
        """Create a new notification and send it to the user."""
        notification = cls.objects.create(
            user=user,
            type=type,
            title=title,
            message=message,
            link=link
        )
        # Send real-time notification if WebSocket is implemented
        return notification

    @classmethod
    def notify_project_assignment(cls, project, provider):
        """Notify provider about project assignment."""
        cls.create_notification(
            user=provider,
            type='project_assigned',
            title='New Project Assignment',
            message=f'You have been assigned to the project: {project.name}',
            link=f'/projects/{project.pk}/'
        )

    @classmethod
    def notify_seo_log_added(cls, seo_log):
        """Notify relevant users about new SEO log."""
        # Notify customer
        cls.create_notification(
            user=seo_log.project.customer.user,
            type='seo_log_added',
            title='New SEO Log Added',
            message=f'New SEO log added for project: {seo_log.project.name}',
            link=f'/seo-logs/{seo_log.pk}/'
        )
        # Notify other providers
        for provider in seo_log.project.providers.exclude(id=seo_log.created_by.id):
            cls.create_notification(
                user=provider,
                type='seo_log_added',
                title='New SEO Log Added',
                message=f'New SEO log added for project: {seo_log.project.name}',
                link=f'/seo-logs/{seo_log.pk}/'
            )

    @classmethod
    def notify_report_generated(cls, report, project):
        """Notify customer about new report."""
        cls.create_notification(
            user=project.customer.user,
            type='report_generated',
            title='New Report Available',
            message=f'A new SEO report is available for project: {project.name}',
            link=f'/reports/{project.pk}/'
        )

    @classmethod
    def notify_project_completed(cls, project):
        """Notify all relevant users about project completion."""
        # Notify customer
        cls.create_notification(
            user=project.customer.user,
            type='project_completed',
            title='Project Completed',
            message=f'Project completed: {project.name}',
            link=f'/projects/{project.pk}/'
        )
        # Notify providers
        for provider in project.providers.all():
            cls.create_notification(
                user=provider,
                type='project_completed',
                title='Project Completed',
                message=f'Project completed: {project.name}',
                link=f'/projects/{project.pk}/'
            )

    @classmethod
    def notify_file_uploaded(cls, file, seo_log):
        """Notify relevant users about file upload."""
        # Notify customer
        cls.create_notification(
            user=seo_log.project.customer.user,
            type='file_uploaded',
            title='New File Uploaded',
            message=f'New file uploaded for project: {seo_log.project.name}',
            link=f'/seo-logs/{seo_log.pk}/'
        )
        # Notify other providers
        for provider in seo_log.project.providers.exclude(id=seo_log.created_by.id):
            cls.create_notification(
                user=provider,
                type='file_uploaded',
                title='New File Uploaded',
                message=f'New file uploaded for project: {seo_log.project.name}',
                link=f'/seo-logs/{seo_log.pk}/'
            )
