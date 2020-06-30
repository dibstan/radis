# Generated by Django 3.0.7 on 2020-06-26 16:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('batch_transfer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BatchTransferItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_id', models.CharField(max_length=16)),
                ('patient_id', models.CharField(max_length=64, null=True)),
                ('patient_name', models.CharField(max_length=256, null=True)),
                ('patient_birth_date', models.DateField()),
                ('study_date', models.DateField()),
                ('modality', models.CharField(max_length=16)),
                ('pseudonym', models.CharField(max_length=256, null=True)),
                ('status_code', models.CharField(choices=[('SU', 'Success'), ('WA', 'Warning'), ('ER', 'Error')], max_length=2, null=True)),
                ('status_message', models.CharField(max_length=256, null=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='batch_transfer.BatchTransferJob')),
            ],
            options={
                'unique_together': {('request_id', 'job')},
            },
        ),
        migrations.DeleteModel(
            name='BatchTransferRequest',
        ),
    ]