from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('provider', 'Provider'),
        ('client', 'Client'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')

class Client(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    website = models.URLField()
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client.name} - {self.name}"

class SEOLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateField()
    on_page_work = models.TextField()
    off_page_work = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.name} - {self.date}"

class ReportSection(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
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
