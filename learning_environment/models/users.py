"""
Models for user related data.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """
    This User is used to possibly change the authentication down the line
    """
    pass


class Profile(models.Model):
    """A profile extends the django user class with additional fields, like a nickname"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(default="Llama", max_length=64)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a profile if a user is created"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Automatically save the profile if the user data is saved"""
    instance.profile.save()
