# Generated by Django 4.1.4 on 2022-12-15 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_environment', '0010_merge_20221213_2156'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_day',
            field=models.DateField(null=True),
        ),
    ]
