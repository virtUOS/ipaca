# Generated by Django 4.1.1 on 2022-11-02 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_environment', '0006_remove_profile_level_lesson_series_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='start',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='wrapup',
            field=models.TextField(null=True),
        ),
    ]
