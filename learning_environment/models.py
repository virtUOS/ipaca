from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    '''
    This User is used to possibly change the authentication down the line
    '''
    pass


class Answer(models.Model):
    content = models.TextField(null=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.content


class Task(models.Model):
    '''
    There are multiple Tasks within a lesson
    The Tasks are subclassed according to their interaction type


    interaction: in what way does the Leaner give their answer
    type: which of the three different types does the task have, useful for later defining order
    title: the unique identifier of the Task
    paragraph_shown: if true the paragraph for the corresponding lesson will be displayed
    '''
    TASK_TYPE = [
        ('R', 'Reading'),
        ('GS', 'Grammar/Style'),
        ('V', 'Vocabulary')
    ]

    INTERACTION_TYPE = [
        ('SC', 'single choice')
    ]

    interaction = models.CharField(max_length=100, choices=INTERACTION_TYPE, default=('SC', 'single choice'))

    type = models.CharField(max_length=100, choices=TASK_TYPE)

    title = models.CharField(max_length=255, unique=True)
    paragraph_shown = models.BooleanField(default=False)
    answers = models.ManyToManyField(Answer, through='TaskAnswer')

    def __str__(self):
        """String for representing the Model object."""
        return self.title

class SingleChoice(Task):
    '''
    A task,

    question: store the instructions or questions given to the Learner, e.g., "Choose the fruit from the list"
    option: multiple options seperated by | ,e.g., "Potato | Apple | Carrot"
    answer: denotes for every option whether it is True: 1 or False: 0 ,e.g., " 0 | 1 | 0"

    '''

    Task.interaction = models.CharField(max_length=100, choices=[('SC', 'single choice')])
    question = models.TextField()



class TaskAnswer(models.Model):
    '''
    Connecting the answers to their corresponding tasks
    Any answer might only have one corresponding task

    feedback: the feedback conneted to this answer,e.g. "This is correct"/"This is wrong because of..."
    value: can be used to order the answers
    '''

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    feedback = models.TextField(null=True)

    value = models.IntegerField(null=True) # value can be used to either give an order or used binary with correct = 1 and false = 0

    class Meta:
        unique_together = ['task', 'answer']



class Lesson(models.Model):
    '''
    A selected collection of task
    Comes which has a paragraph

    name: unique identifier
    paragraph: piece of written academic text to read
    tasks: tasks belonging to the lesson
    '''
    name = models.CharField(max_length=255, unique=True)
    paragraph = models.TextField()
    tasks = models.ManyToManyField(Task, through='TaskOrder')

    def __str__(self):
        """String for representing the Model object."""
        return self.name

class Learner(User):
    '''
    The User which uses the app
    '''

    # user = models.OneToOneField(User, on_delete=models.CASCADE, null=
    tasks = models.ManyToManyField(Task, through='Learner_Task')
    lessons = models.ManyToManyField(Lesson, through='Learner_Lesson')

    def __str__(self):
        """String for representing the Model object."""
        return self.username

class TaskOrder(models.Model):
    '''
    connection between lesson and task
    Each task and lesson can only be match once

    order: in which order should the task be done
    '''
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    order = models.IntegerField()

    class Meta:
        unique_together = ['task', 'lesson']

    def __str__(self):
        """String for representing the Model object."""
        return self.lesson.name + '_'+ self.task.title + '_' + str(self.order)


class Module(models.Model):
    '''
    The 3 main modules. Biggest building block of the learning environment
    '''

    LEVEL = [
        ('1', 'Textbook'),
        ('2', 'General texts'),
        ('3', 'Spezialized Texts')
    ]
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=100, choices=LEVEL, unique=True)
    lesson = models.ManyToManyField(Lesson, through='LessonOrder')

    def __str__(self):
        """String for representing the Model object."""
        return self.name

class LessonOrder(models.Model):
    '''
    connection between module and lesson


    order: in which order should the lesson be done
    '''

    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    order = models.IntegerField()

    def __str__(self):
        """String for representing the Model object."""
        return self.module.name + '_' + self.lesson.name

class Learner_Lesson(models.Model):
    '''
    Connection between the Learner and Lessons

    open: Can the Leaner do this Lesson?
    order: in which order are the lessons presented
    '''
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    open = models.BooleanField(default=True)

    class Meta:
        unique_together = ['learner', 'lesson']

    def __str__(self):
        """String for representing the Model object."""
        return self.learner.username + '_'+ self.lesson.name


class Learner_Task(models.Model):
    '''
    Connection between the Learner and Tasks

    open: Can the Leaner do this Task?

    '''
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)



    open = models.BooleanField(default=True)
    correct = models.BooleanField(null=True)

    class Meta:
        unique_together = ['learner', 'task']

    def __str__(self):
        """String for representing the Model object."""
        return self.learner.username + '_'+ self.task.title