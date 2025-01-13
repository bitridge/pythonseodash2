from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import SEOLog, Report, ReportAttachment, SEOLogFile
import os

@receiver(post_delete, sender=SEOLogFile)
def auto_delete_seo_log_file_on_delete(sender, instance, **kwargs):
    """
    Delete file from filesystem when corresponding SEOLogFile object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

@receiver(post_delete, sender=ReportAttachment)
def auto_delete_report_attachment_on_delete(sender, instance, **kwargs):
    """
    Delete file from filesystem when corresponding ReportAttachment object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path) 