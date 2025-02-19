# Generated by Django 5.1.4 on 2024-12-27 08:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_seolog_options_remove_seolog_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='providers',
            field=models.ManyToManyField(blank=True, limit_choices_to={'role': 'provider'}, related_name='assigned_projects', to=settings.AUTH_USER_MODEL),
        ),
    ]
