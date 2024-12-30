from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_update_client_to_customer'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Client',
            new_name='Customer',
        ),
    ] 