# Generated by Django 4.1.1 on 2022-10-26 11:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("learning_environment", "0005_alter_task_interaction"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="level",
        ),
        migrations.AddField(
            model_name="lesson",
            name="series",
            field=models.CharField(default="General", max_length=255),
        ),
        migrations.CreateModel(
            name="ProfileSeriesLevel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("series", models.CharField(default="General", max_length=256)),
                ("level", models.IntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "series")},
            },
        ),
        migrations.AlterField(
            model_name='profileserieslevel',
            name='series',
            field=models.CharField(default='Academic English', max_length=256),
        ),
    ]
