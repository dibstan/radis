# Generated by Django 5.0.6 on 2024-07-10 14:54

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("reports", "0011_report_search_vector"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="report",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="reports_rep_search__63862e_gin"
            ),
        ),
    ]
