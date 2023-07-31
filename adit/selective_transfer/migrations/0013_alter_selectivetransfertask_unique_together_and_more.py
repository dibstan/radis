# Generated by Django 4.2.3 on 2023-07-27 15:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("selective_transfer", "0012_convert_json_to_text"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="selectivetransfertask",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="selectivetransfertask",
            constraint=models.UniqueConstraint(
                fields=("job", "task_id"), name="selectivetransfertask_unique_task_id_per_job"
            ),
        ),
    ]