"""ipaca Tutor Model

The tutor model is able to determine appropriate actions for a given learner. (E.g. generate a 'next task')

"""

import random
from learning_environment.models import Lesson, Task

class NoTaskAvailableError(Exception):
    pass

class Tutormodel:

    def __init__(self, learner):
        """Initializes the tutor model for a given learner.

        learner: User object"""

        self.learner = learner

    def next_task(self):
        """Pick a next task for the learner."""

        num_tasks = Task.objects.count()
        if num_tasks == 0:
            raise NoTaskAvailableError("No tasks in the database.")
        task = Task.objects.all()[random.randint(0, num_tasks-1)]
        return task
