# Generated by Django 4.1.4 on 2022-12-09 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_environment', '0007_profile_gamification_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='gamification_level',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='profile',
            name='total_XP',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gamification_active',
            field=models.BooleanField(default=False),
        ),
    ]
