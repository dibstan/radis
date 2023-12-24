# Generated by Django 4.2.8 on 2023-12-20 12:12

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import radis.core.validators


class Migration(migrations.Migration):
    replaces = [
        ("reports", "0001_initial"),
        ("reports", "0002_report"),
        ("reports", "0003_remove_report_institutes_report_groups"),
    ]

    initial = True

    dependencies = [
        ("accounts", "0005_institute"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReportsAppSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("locked", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name_plural": "Reports app settings",
            },
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("document_id", models.CharField(max_length=128, unique=True)),
                ("pacs_aet", models.CharField(max_length=16)),
                ("pacs_name", models.CharField(max_length=64)),
                (
                    "patient_id",
                    models.CharField(
                        max_length=64,
                        validators=[
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid backslash character",
                                regex="\\\\",
                            ),
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid control characters.",
                                regex="[\\f\\n\\r]",
                            ),
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid wildcard characters.",
                                regex="[\\*\\?]",
                            ),
                        ],
                    ),
                ),
                ("patient_birth_date", models.DateField()),
                (
                    "patient_sex",
                    models.CharField(
                        max_length=1, validators=[radis.core.validators.validate_patient_sex]
                    ),
                ),
                (
                    "study_instance_uid",
                    models.CharField(
                        max_length=64,
                        validators=[
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid backslash character",
                                regex="\\\\",
                            ),
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid control characters.",
                                regex="[\\f\\n\\r]",
                            ),
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid wildcard characters.",
                                regex="[\\*\\?]",
                            ),
                        ],
                    ),
                ),
                (
                    "accession_number",
                    models.CharField(
                        blank=True,
                        max_length=64,
                        validators=[
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid backslash character",
                                regex="\\\\",
                            ),
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid control characters.",
                                regex="[\\f\\n\\r]",
                            ),
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid wildcard characters.",
                                regex="[\\*\\?]",
                            ),
                        ],
                    ),
                ),
                ("study_description", models.CharField(blank=True, max_length=64)),
                ("study_datetime", models.DateTimeField()),
                (
                    "series_instance_uid",
                    models.CharField(
                        max_length=64,
                        validators=[
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid backslash character",
                                regex="\\\\",
                            ),
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid control characters.",
                                regex="[\\f\\n\\r]",
                            ),
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid wildcard characters.",
                                regex="[\\*\\?]",
                            ),
                        ],
                    ),
                ),
                (
                    "modalities_in_study",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=16), size=None
                    ),
                ),
                (
                    "sop_instance_uid",
                    models.CharField(
                        max_length=64,
                        validators=[
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid backslash character",
                                regex="\\\\",
                            ),
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid control characters.",
                                regex="[\\f\\n\\r]",
                            ),
                            django.core.validators.RegexValidator(
                                inverse_match=True,
                                message="Contains invalid wildcard characters.",
                                regex="[\\*\\?]",
                            ),
                        ],
                    ),
                ),
                (
                    "references",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.URLField(), size=None
                    ),
                ),
                ("body", models.TextField()),
                ("groups", models.ManyToManyField(related_name="reports", to="auth.group")),
            ],
        ),
    ]