# Generated by Django 3.1.3 on 2021-02-16 13:26

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("continuous_transfer", "0004_init_task_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="continuoustransfertask",
            name="celery_task_id",
            field=models.CharField(default=uuid.uuid4(), max_length=255),
            preserve_default=False,
        ),
    ]