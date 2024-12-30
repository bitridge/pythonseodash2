# Generated by Django 5.1.4 on 2024-12-30 08:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_rename_project_client_to_customer'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reportsection',
            options={'ordering': ['priority', 'created_at']},
        ),
        migrations.AlterModelOptions(
            name='seolog',
            options={'ordering': ['-date'], 'verbose_name': 'SEO Log', 'verbose_name_plural': 'SEO Logs'},
        ),
        migrations.RemoveField(
            model_name='reportsection',
            name='image',
        ),
        migrations.RemoveField(
            model_name='reportsection',
            name='order',
        ),
        migrations.RemoveField(
            model_name='seolog',
            name='off_page_description',
        ),
        migrations.RemoveField(
            model_name='seolog',
            name='off_page_work',
        ),
        migrations.RemoveField(
            model_name='seolog',
            name='on_page_description',
        ),
        migrations.RemoveField(
            model_name='seolog',
            name='on_page_work',
        ),
        migrations.AddField(
            model_name='reportsection',
            name='priority',
            field=models.PositiveIntegerField(default=1, help_text='Priority determines page order (1 starts on first page)'),
        ),
        migrations.AddField(
            model_name='seolog',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='seolog',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='seolog',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='seolog',
            name='work_type',
            field=models.CharField(choices=[('on_page', 'On-Page SEO'), ('off_page', 'Off-Page SEO'), ('technical', 'Technical SEO'), ('content', 'Content Optimization'), ('analytics', 'Analytics & Tracking'), ('other', 'Other')], default='other', max_length=20),
        ),
        migrations.AlterField(
            model_name='reportsection',
            name='content',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='reportsection',
            name='files',
            field=models.ManyToManyField(blank=True, to='core.seologfile'),
        ),
        migrations.AlterField(
            model_name='reportsection',
            name='seo_logs',
            field=models.ManyToManyField(blank=True, to='core.seolog'),
        ),
        migrations.AlterField(
            model_name='reportsection',
            name='title',
            field=models.CharField(max_length=200),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_draft', models.BooleanField(default=True)),
                ('version', models.PositiveIntegerField(default=1)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.project')),
            ],
        ),
        migrations.CreateModel(
            name='ReportAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='report_attachments/%Y/%m/')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('file_type', models.CharField(max_length=50)),
                ('file_size', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('report_section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='core.reportsection')),
            ],
        ),
        migrations.CreateModel(
            name='AttachmentAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accessed_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('attachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.reportattachment')),
            ],
            options={
                'ordering': ['-accessed_at'],
            },
        ),
        migrations.CreateModel(
            name='ReportSectionOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('page_break_before', models.BooleanField(default=True)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.report')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.reportsection')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('report', 'order')},
            },
        ),
        migrations.AddField(
            model_name='report',
            name='sections',
            field=models.ManyToManyField(through='core.ReportSectionOrder', to='core.reportsection'),
        ),
        migrations.CreateModel(
            name='ReportVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_number', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('changes', models.TextField()),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='report_versions/%Y/%m/')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='core.report')),
            ],
            options={
                'ordering': ['-version_number'],
                'unique_together': {('report', 'version_number')},
            },
        ),
    ]
