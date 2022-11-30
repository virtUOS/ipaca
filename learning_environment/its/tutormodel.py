"""ipaca Tutor Model
The tutor model is able to determine appropriate actions for a given learner. (E.g. generate a 'next task')
"""

import random
from learning_environment.models import Lesson, Task, ProfileSeriesLevel


class NoTaskAvailableError(Exception):
    pass


class Tutormodel:

    def __init__(self, learner):
        """Initializes the tutor model for a given learner.
        learner: User object"""
        self.learner = learner

    def next_task(self, request):
        """Pick a next task for the learner.
        Returns tuple:
        (STATE, lesson, task)
        """

        order = ['START', 'R', 'GS', 'V', 'WRAPUP']

        # determine the current lesson series
        series = request.session.get('lesson_series', 'General')

        # pick a lesson
        current_lesson_id = request.session.get('current_lesson', None)
        if current_lesson_id:
            try:
                lesson = Lesson.objects.get(pk=current_lesson_id)
            except Lesson.DoesNotExist:
                raise Exception("Lesson from session does not exist: {}!".format(current_lesson_id))
        else:
            lesson = self.start_lesson(series)
            request.session['current_lesson'] = lesson.id
            request.session['current_lesson_todo'] = order[:]
            request.session.modified = True

        # pick a task
        while 1:
            next_type = request.session['current_lesson_todo'][0]
            request.session.modified = True
            if next_type == 'START':
                return next_type, lesson, None
            elif next_type == 'WRAPUP':
                return next_type, lesson, None
            else:  # pick random task of fitting type
                tasks = Task.objects.filter(lesson=lesson, type=next_type)
                cnt = tasks.count()
                if cnt == 0:
                    request.session['current_lesson_todo'].pop(0)  # if we don't have such a task, remove it
                    continue  # next state
                task = tasks[random.randint(0, cnt-1)]
                return next_type, lesson, task

        # num_tasks = Task.objects.filter(lesson=lesson).count()
        # if num_tasks == 0:
        #   raise NoTaskAvailableError("No tasks in the database.")
        # task = Task.objects.all()[random.randint(0, num_tasks-1)]
        # return task

    def start_lesson(self, series):
        try:
            current_level = ProfileSeriesLevel.objects.get(user=self.learner, series=series).level
        except ProfileSeriesLevel.DoesNotExist:
            ProfileSeriesLevel.objects.create(user=self.learner, series=series, level=0)
            current_level = 0

        lesson = Lesson.objects.filter(series=series).order_by("lesson_id")[current_level]
        return lesson
