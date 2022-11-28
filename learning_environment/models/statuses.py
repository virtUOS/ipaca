"""
Models for all the data that contain status information in some sense.
"""
from django.db import models

from learning_environment.models import User, Lesson, Task


class ProfileSeriesLevel(models.Model):
    """A user's level within a series"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    series = models.CharField(max_length=256, default='General')
    level = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'series')  # ensure there's only one level per user per series


class Solution(models.Model):
    """The solution of a task for a given user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    solved = models.BooleanField()
    analysis = models.JSONField()


class UserLesson(models.Model):
    """A user's status in a lesson."""
    # TODO: Check if we can remove it because it is not used
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    started = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True)

    class Meta:
        unique_together = ['user', 'lesson']


class LearnerStatus(models.Model):
    # TODO: Check if we can remove it because it is not used, similar to UserLesson
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    current_lesson = models.ForeignKey(Lesson, null=True, on_delete=models.SET_NULL)
