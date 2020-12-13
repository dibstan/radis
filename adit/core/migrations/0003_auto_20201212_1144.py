# Generated by Django 3.1.3 on 2020-12-12 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20201129_1531'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transferjob',
            options={'permissions': [('can_transfer_directly', 'Can transfer directly (without scheduling).')]},
        ),
        migrations.AddField(
            model_name='transferjob',
            name='transfer_directly',
            field=models.BooleanField(default=False),
        ),
    ]