from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('provider', 'Provider'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

class Client(models.Model):
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
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    providers = models.ManyToManyField(CustomUser, related_name='assigned_projects', blank=True, limit_choices_to={'role': 'provider'})

    def __str__(self):
        return f"{self.client.name} - {self.name}"

class SEOLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_logs')
    on_page_work = models.BooleanField(default=False)
    off_page_work = models.BooleanField(default=False)
    on_page_description = models.TextField(blank=True)
    off_page_description = models.TextField(blank=True)
    providers = models.ManyToManyField(CustomUser, related_name='assigned_logs', blank=True)

    def __str__(self):
        return f"{self.project.name} - {self.date}"

    class Meta:
        ordering = ['-date']

class SEOLogFile(models.Model):
    WORK_TYPE_CHOICES = [
        ('on_page', 'On-Page'),
        ('off_page', 'Off-Page'),
    ]

    seo_log = models.ForeignKey(SEOLog, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='seo_logs/%Y/%m/%d/')
    work_type = models.CharField(max_length=10, choices=WORK_TYPE_CHOICES)
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_size = models.IntegerField()  # Size in bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name

    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = self.file.name
        if not self.file_type:
            # Get file type from extension
            ext = self.file.name.split('.')[-1].lower()
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
        if not self.file_size:
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
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)  # Custom content
    seo_logs = models.ManyToManyField(SEOLog, blank=True, related_name='report_sections')
    files = models.ManyToManyField(SEOLogFile, blank=True, related_name='report_sections')
    image = models.ImageField(upload_to='report_images/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.name} - {self.title}"

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
        # Notify client
        cls.create_notification(
            user=seo_log.project.client.user,
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
        """Notify client about new report."""
        cls.create_notification(
            user=project.client.user,
            type='report_generated',
            title='New Report Available',
            message=f'A new SEO report is available for project: {project.name}',
            link=f'/reports/{project.pk}/'
        )

    @classmethod
    def notify_project_completed(cls, project):
        """Notify all relevant users about project completion."""
        # Notify client
        cls.create_notification(
            user=project.client.user,
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
        # Notify client
        cls.create_notification(
            user=seo_log.project.client.user,
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
