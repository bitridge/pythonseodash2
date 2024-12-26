from django.db import migrations, models
import django.db.models.deletion

def set_default_created_by(apps, schema_editor):
    SEOLog = apps.get_model('core', 'SEOLog')
    CustomUser = apps.get_model('core', 'CustomUser')
    
    # Get the first admin user or create one if none exists
    admin_user = CustomUser.objects.filter(role='admin').first()
    if not admin_user:
        admin_user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin',
            role='admin'
        )
    
    # Set the default user for all SEO logs without a created_by user
    SEOLog.objects.filter(created_by__isnull=True).update(created_by=admin_user)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(set_default_created_by),
        migrations.AlterField(
            model_name='seolog',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='created_logs',
                to='core.customuser'
            ),
        ),
    ] 