# Generated by Django 4.2 on 2025-05-27 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0015_evento_creator'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
