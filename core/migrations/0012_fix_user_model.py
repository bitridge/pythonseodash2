from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_reportsection_options_alter_seolog_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='user_permissions',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('admin', 'Administrator'), ('provider', 'Provider'), ('customer', 'Customer')], default='customer', max_length=10),
        ),
    ] 