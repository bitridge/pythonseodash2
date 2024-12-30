from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_rename_client_to_customer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='client',
            new_name='customer',
        ),
    ] 