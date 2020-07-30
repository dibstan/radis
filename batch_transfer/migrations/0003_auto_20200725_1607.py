# Generated by Django 3.0.7 on 2020-07-25 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batch_transfer', '0002_auto_20200725_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchtransferrequest',
            name='status',
            field=models.CharField(choices=[('UN', 'Unprocessed'), ('SU', 'Success'), ('FA', 'Failure')], default='UN', max_length=2),
        ),
    ]