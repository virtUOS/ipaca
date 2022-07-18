from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass



class Task(models.Model):
    uuid = models.UUIDField()

    TASK_TYPE = [
        ('R', 'Reading'),
        ('GS', 'Grammar/Style'),
        ('V', 'Vocabulary')
    ]

    type = models.CharField(max_length=100, choices=TASK_TYPE)

    title = models.CharField(max_length=500)
    description = models.TextField(null=True)
    paragraph_shown = models.BooleanField(default=False)





class SingleChoice(Task):
    text_element = models.TextField()  # this is for storing the question/input/for closes
    question = models.TextField()
    options = models.TextField()  # seperator: |
    answers = models.TextField()  # seperator: |


class Lesson(models.Model):
    name = models.CharField(max_length=255)
    paragraph = models.TextField()
    task = models.ManyToManyField(Task, through='TaskOrder')


class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tasks = models.ManyToManyField(Task, through='Learner_Task')
    lessons = models.ManyToManyField(Lesson, through='Learner_Lesson')



class TaskOrder(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    order = models.IntegerField()


class Module(models.Model):
    LEVEL = [
        ('1', 'Textbook'),
        ('2', 'General texts'),
        ('3', 'Spezialized Texts')
    ]

    level = models.CharField(max_length=100, choices=LEVEL)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)


class Learner_Lesson(models.Model):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    open = models.BooleanField(default=True)
    order = models.IntegerField()

    class Meta:
        unique_together = ['learner', 'lesson']


class Learner_Task(models.Model):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    open = models.BooleanField(default=True)



    class Meta:
        unique_together = ['learner', 'task']
