from django.db import models
from django.contrib.auth.models import AbstractUser
from learning_environment.its.base import Json5ParseException
from learning_environment.its.tasks import TaskTypeFactory
#from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_gamification.models import GamificationInterface
from django.utils import timezone
import json5


class User(AbstractUser):
    """
    This User is used to possibly change the authentication down the line
    """
    pass


class Profile(models.Model):
    """A profile extends the djanog user class with additional fields, like a nickname"""
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


class ProfileSeriesLevel(models.Model):
    """A user's level within a series"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    series = models.CharField(max_length=256, default='Academic English')
    level = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'series')  # ensure there's only one level per user per series



class Lesson(models.Model):
    """
    A selected collection of task
    Comes which has a paragraph

    name: unique identifier
    paragraph: piece of written academic text to read
    tasks: tasks belonging to the lesson
    """
    name = models.CharField(max_length=255)
    lesson_id = models.SlugField(max_length=64)
    series = models.CharField(max_length=255, default='Academic English')
    author = models.CharField(max_length=256)
    text = models.TextField()
    text_source = models.CharField(max_length=1024, null=True)
    text_licence = models.CharField(max_length=1024, null=True)
    text_url = models.URLField(null=True)
    start = models.TextField(null=True)  # text to be displayed before the lesson starts
    wrapup = models.TextField(null=True)  # text to be displyed after the lesson has been finished
    json5 = models.TextField(null=True)

    @classmethod
    def check_json5(cls, lesson_json5):
        """Check if a JSON5 representation of a lesson is valid."""
        try:
            lesson = json5.loads(lesson_json5)
        except ValueError as err:
            raise Json5ParseException("Error in JSON5 code Error message: '{}'".format(err))

        if not isinstance(lesson, dict):
            raise Json5ParseException("Lesson code must be a dictionary.")

        # Checks
        # Mandatory fields
        for lesson_field in ["name", "id", "text", "text_source", "text_licence", "text_url", "author", "tasks"]:
            if lesson_field not in lesson:
                raise Json5ParseException('Field "{}" is missing'.format(lesson_field))
            if not lesson[lesson_field]:
                raise Json5ParseException('Field "{}" is empty'.format(lesson_field))

        # Optional fields must not be empty
        for lesson_field in ['series', 'start', 'wrapup']:
            if lesson_field in lesson and not lesson[lesson_field]:
                raise Json5ParseException('Field "{}" is empty'.format(lesson_field))

        task_num = 0
        for t in lesson["tasks"]:
            task_num += 1
            Task.check_json5(t, task_num)
        return True

    @classmethod
    def create_from_json5(cls, lesson_json5):
        cls.check_json5(lesson_json5)

        lesson = json5.loads(lesson_json5)

        # delete old lesson, all its tasks and progress if it already exists
        # TODO: This is most probably not suited for production use! Replace by activation status for lessons
        try:
            Lesson.objects.get(lesson_id=lesson["id"]).delete()
        except Lesson.DoesNotExist:
            pass

        lsn = Lesson(name=lesson["name"],
                     lesson_id=lesson["id"],
                     author=lesson["author"],
                     text=lesson["text"],
                     text_source=lesson["text_source"],
                     text_licence=lesson["text_licence"],
                     text_url=lesson["text_url"],
                     json5=lesson_json5)
        if 'series' in lesson:
            lsn.series = str(lesson['series'])
        if 'start' in lesson:
            lsn.start = str(lesson['start'])
        if 'wrapup' in lesson:
            lsn.wrapup = str(lesson['wrapup'])

        lsn.save()


        for task in lesson["tasks"]:
            Task.create_from_json5(task, lsn)

        return lsn


class Task(models.Model):
    """
    There are multiple Tasks within a lesson
    The Tasks are subclassed according to their interaction type


    interaction: in what way does the Leaner give their answer
    type: which of the three different types does the task have, useful for later defining order
    title: the unique identifier of the Task
    paragraph_shown: if true the paragraph for the corresponding lesson will be displayed
    """
    TASK_TYPE = [
        ('R', 'Reading'),
        ('GS', 'Grammar/Style'),
        ('V', 'Vocabulary')
    ]

    name = models.CharField(max_length=256)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    interaction = models.CharField(max_length=10)
    type = models.CharField(max_length=100, choices=TASK_TYPE)
    primary = models.BooleanField(default=True)
    show_lesson_text = models.BooleanField(default=True)
    question = models.TextField()
    content = models.JSONField()

    @classmethod
    def check_json5(cls, task_json5, task_num=0):

        for task_field in [("name", str, "a string"),
                           ("type", ['R', 'GS', 'V'], "'R', 'GS', 'V'"),
                           ("interaction", TaskTypeFactory.shortcuts(), ','.join(TaskTypeFactory.shortcuts())),
                           ("primary", bool, "true or false"),
                           ("show_lesson_text", bool, "true or false"),
                           ("question", str, "a string")]:
            if task_field[0] not in task_json5:
                raise Json5ParseException(
                    'Field "{}" is missing for task {}'.format(task_field[0], task_num))
            if isinstance(task_field[1], type) and not isinstance(task_json5[task_field[0]], task_field[1]):
                raise Json5ParseException(
                    'Field "{}" for task {} has wrong type, it has to be {}'.format(
                        task_field[0], task_num, task_field[2]))
            elif isinstance(task_field[1], list) and task_json5[task_field[0]] not in task_field[1]:
                raise Json5ParseException('Field "{}" for task {} has wrong value, it has to be one of {}'.format(
                    task_field[0], task_num, task_field[2]))

        # fetch the class for that interaction and let it check the json5 content
        TaskTypeFactory.getClass(task_json5['interaction']).check_json5(task_json5, task_num)

        return True

    @classmethod
    def create_from_json5(cls, task, lesson):
        content = TaskTypeFactory.getClass(task['interaction']).get_content_from_json5(task)
        t = Task(name=task["name"],
                 type=task["type"],
                 interaction=task["interaction"],
                 primary=task["primary"],
                 show_lesson_text=task["show_lesson_text"],
                 question=task["question"],
                 content=content,
                 lesson=lesson
                 )
        t.save()
        return t

    def get_template(self):
        return TaskTypeFactory.getClass(self.interaction).template

    def get_additional_js(self):
        try:
            return TaskTypeFactory.getClass(self.interaction).additional_js
        except AttributeError:
            return ''

class UserLesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    started = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True)

    class Meta:
        unique_together = ['user', 'lesson']


class Solution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    solved = models.BooleanField()
    analysis = models.JSONField()

class LearnerStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    current_lesson = models.ForeignKey(Lesson, null=True, on_delete=models.SET_NULL)

class Streak(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    last_update = models.DateField(default=timezone.now)
    streak_count = models.IntegerField(default=0)


class GamificationUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default="avatarb.png")
    interface = models.ForeignKey(GamificationInterface, on_delete=models.CASCADE)

    def update_streak(self):
        current = timezone.now().date()
        try:
            streak = Streak.objects.filter(user=self.user).latest('last_update')
            delta = current - streak.last_update
            if delta == 0:
                return
            if delta == timezone.timedelta(days=1):
                streak.streak_count += 1
                streak.last_update = current
                streak.save()
            else:
                Streak.objects.create(user=self.user, start_date=current, streak_count=1)

        except Streak.DoesNotExist:
            Streak.objects.create(user=self.user, start_date=current, streak_count=1)

        return True

