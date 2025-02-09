# Generated by Django 4.2 on 2025-02-09 03:16

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0009_alter_evento_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="evento",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
    ]
