from django.db import models
from django.contrib.auth.models import User


class Competency(models.Model):
    """
    Competencies to learn in this app, e.g. reading, summarization...
    """

    type = models.CharField(max_length=250)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Learner(models.Model):
    """
    BasicUser of the learning environment
    """

    user_id = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    competencies = models.ManyToManyField(Competency, through='LearnerCompetency')

    def __str__(self):
        return self.user_id


class LearnerCompetency(models.Model):
    """
    Intermediate model for ManyToMany-Relationship of  Learner and Competency

    """
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE)

    times_seen = models.IntegerField(default=0)
    proficiency = models.IntegerField(default=0)


class TaskType(models.Model):
    """
    Model for capturing the type of the respective task, e.g. single choice, cloze, multiple choice,

    """
    TASK_TYPES = [
        ('sc', 'single choice'),
        ('mc', 'multiple choice')
    ]

    name = models.CharField(max_length=250, choices=TASK_TYPES)


class Text(models.Model):
    TEXT_TYPES = [
        ('TB', 'Textbook'),
        ('JA', 'Journal Article')
    ]

    title = models.CharField(max_length=250)
    topic = models.CharField(max_length=250)
    type = models.CharField(max_length=250, choices=TEXT_TYPES)
    author = models.CharField(max_length=250)
    source = models.CharField(max_length=250)
    content = models.TextField(max_length=100000)
    license = models.CharField(max_length=250)


class Task(models.Model):
    """
    Instance of a complete task

    """

    type = models.ManyToManyField(TaskType)
    competency = models.ManyToManyField(Competency, through='CompetencyTask')
    difficulty = models.IntegerField()

    text = models.ForeignKey(Text, on_delete=models.CASCADE)

    options = models.CharField(max_length=100)
    solution = models.CharField(max_length=100)

    def __str__(self):
        return self.content


class CompetencyTask(models.Model):
    """
    Intermediate model for ManyToMany-Relationship of Competency and Tasks

    Info about the level of the competency
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE)

    # Within this competency which level is this?
    level = models.IntegerField()  # TODO determine Field type numerical or character for CEFR
