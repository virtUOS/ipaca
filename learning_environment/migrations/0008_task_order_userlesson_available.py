# Generated by Django 4.2.6 on 2023-11-10 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_environment', '0007_lesson_start_lesson_wrapup'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='order',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userlesson',
            name='available',
            field=models.BooleanField(default=False),
        ),
    ]
