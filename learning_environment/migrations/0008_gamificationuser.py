# Generated by Django 4.2 on 2023-05-21 19:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_gamification', '0014_alter_badge_id_alter_badgedefinition_id_and_more'),
        ('learning_environment', '0007_lesson_start_lesson_wrapup'),
    ]

    operations = [
        migrations.CreateModel(
            name='GamificationUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interface', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_gamification.gamificationinterface')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]