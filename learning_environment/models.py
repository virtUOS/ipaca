from django.db import models
from django.contrib.auth.models import User

class Module(models.Model):

    LEVEL = [
        ('1','Textbook'),
        ('2','General texts'),
        ('3','Spezialized Texts')
    ]

    level = models.CharField(max_length=100, choices=LEVEL)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

class Lesson(models.Model):

    paragraph = models.TextField()
    task = models.ManyToManyField(Task, through=TaskOrder)

class Task(models.Model):

    TASK_TYPE = [
        ('R','Reading'),
        ('GS','Grammar/Style'),
        ('V', 'Vocabulary')
    ]


    #TODO integrate Ellas list
    INTERACTION_TYPE = [
        ('SC', 'single choice'),
        ('...','...')
    ]

    type = models.CharField(max_length=100, choices=TASK_TYPE)
    interaction = models.CharField(max_length=100, choices=INTERACTION_TYPE)

class TaskOrder(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    task = models.ForeignKey(Task,on_delete=models.CASCADE)
    order = models.IntegerField()