# Generated by Django 4.2 on 2025-02-09 04:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0012_evento_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="entrada",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
