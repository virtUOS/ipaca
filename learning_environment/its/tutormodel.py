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

    def next_task(self, request, start_new_lesson=None):
        """Pick a next task for the learner.
        Returns tuple:
        (STATE, lesson, task)
        """

        order = ['START', 'TASKS', 'WRAPUP']
        # determine the current lesson series
        series = request.session.get('lesson_series', 'General')
        # pick a lesson
        current_lesson = request.session.get('current_lesson', None)
        # start a new lession because: a) explicitly requested, b) no current lesson, c) current lesson is corrupted
        if start_new_lesson or not current_lesson or not 'id' in current_lesson or not 'todo' in current_lesson or not 'next_task' in current_lesson:
            if not start_new_lesson:
                lesson = self.start_lesson(series)  # let tutormodel pick a new lesson
            else:
                lesson = start_new_lesson  # start the lesson expicitly passed
            request.session['current_lesson'] = {'id': lesson.id, 'todo': order[:], 'next_task': 0 }
            current_lesson = request.session['current_lesson']
            request.session.modified = True
        else:  # continue a lession
            try:
                lesson = Lesson.objects.get(pk=current_lesson['id'])
            except Lesson.DoesNotExist:
                raise Exception("Lesson from session does not exist: {}!".format(current_lesson_id))

        # pick a task
        while 1:
            next_type = current_lesson['todo'][0]
            request.session.modified = True
            if next_type == 'START':
                return next_type, lesson, None
            elif next_type == 'WRAPUP':
                return next_type, lesson, None
            else:  # pick the next task for the lesson
                next_task = current_lesson['next_task']
                tasks = Task.objects.filter(lesson=lesson, order=next_task)
                cnt = tasks.count()
                if cnt == 0:
                    request.session['current_lesson']['todo'].pop(0)  # if we don't have any tasks left, remove current type
                    request.session.modified = True
                    continue  # next state
                task = tasks[0]
                request.session['current_lesson']['next_task'] += 1  # increase order for next task
                request.session.modified = True
                return next_type, lesson, task


    def start_lesson(self, series):
        try:
            current_level = ProfileSeriesLevel.objects.get(user=self.learner, series=series).level
        except ProfileSeriesLevel.DoesNotExist:
            ProfileSeriesLevel.objects.create(user=self.learner, series=series, level=0)
            current_level = 0

        lesson = Lesson.objects.filter(series=series).order_by("lesson_id")[current_level]
        return lesson
