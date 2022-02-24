# Generated by Django 4.0.2 on 2022-02-24 08:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('batch_transfer', '0009_rename_batch_ids_batchtransfertask_lines'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchtransferjob',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_jobs', to=settings.AUTH_USER_MODEL),
        ),
    ]
