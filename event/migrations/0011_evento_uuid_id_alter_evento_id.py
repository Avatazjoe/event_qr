# Generated by Django 4.2 on 2025-02-09 03:20

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0010_alter_evento_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="evento",
            name="uuid_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="evento",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
