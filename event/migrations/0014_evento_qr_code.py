# Generated by Django 4.2 on 2025-02-10 02:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0013_entrada_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="evento",
            name="qr_code",
            field=models.ImageField(blank=True, null=True, upload_to="qrcodes/"),
        ),
    ]
