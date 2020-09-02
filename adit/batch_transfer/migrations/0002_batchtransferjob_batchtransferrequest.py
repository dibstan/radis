# Generated by Django 3.1 on 2020-08-31 00:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('batch_transfer', '0001_initial'),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BatchTransferJob',
            fields=[
                ('transferjob_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.transferjob')),
                ('project_name', models.CharField(max_length=150)),
                ('project_description', models.TextField(max_length=2000)),
            ],
            options={
                'permissions': (('cancel_batchtransferjob', 'Can cancel batch transfer job'),),
            },
            bases=('main.transferjob',),
        ),
        migrations.CreateModel(
            name='BatchTransferRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_id', models.PositiveIntegerField()),
                ('patient_id', models.CharField(blank=True, max_length=64, null=True)),
                ('patient_name', models.CharField(blank=True, max_length=324, null=True)),
                ('patient_birth_date', models.DateField()),
                ('accession_number', models.CharField(blank=True, max_length=16, null=True)),
                ('study_date', models.DateField()),
                ('modality', models.CharField(max_length=16)),
                ('pseudonym', models.CharField(blank=True, max_length=324, null=True)),
                ('status', models.CharField(choices=[('PE', 'Pending'), ('IP', 'In Progress'), ('CA', 'Canceled'), ('SU', 'Success'), ('FA', 'Failure')], default='PE', max_length=2)),
                ('message', models.TextField(blank=True, null=True)),
                ('processed_at', models.DateTimeField(null=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='batch_transfer.batchtransferjob')),
            ],
            options={
                'unique_together': {('request_id', 'job')},
            },
        ),
    ]