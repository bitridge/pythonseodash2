# Generated by Django 5.1.4 on 2024-12-30 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_report_sections'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='keep_as_draft',
            field=models.BooleanField(default=True, help_text='Keep new reports as draft by default'),
        ),
    ]
