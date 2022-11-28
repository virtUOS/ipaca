"""
The base tutor model that is able to determine appropriate actions for a given learner (e.g. generate a 'next task').
It can be extended to select tasks differently.
"""

import random

from typing import List, Tuple

from learning_environment.models import Lesson, Task, ProfileSeriesLevel, User


class BaseTutorModel:

    def __init__(self, learner: User):
        """Initializes the tutor model for a given learner.
        learner: User object"""
        self.learner = learner

    def next_step(self, request) -> Tuple[str, Lesson, Task]:
        """
        Prepares the next step in the current lesson and returns it.
        Returns tuple:
        (STATE, lesson, task)
        """
        lesson = self._get_current_lesson(request)
        next_type, task = self._get_next_step(request, lesson)
        return next_type, lesson, task

    def _get_current_lesson(self, request) -> Lesson:
        """Returns the current lesson."""
        # try to get the current session
        current_lesson_id = request.session.get('current_lesson', None)
        if current_lesson_id:
            try:
                lesson = Lesson.objects.get(pk=current_lesson_id)
            except Lesson.DoesNotExist:
                raise Exception("Lesson from session does not exist: {}!".format(current_lesson_id))
        # otherwise start a new lesson for the current series
        else:
            # determine the current lesson series
            series = request.session.get('lesson_series', 'General')
            # and start a new lesson for it
            lesson = self._start_lesson(series)

            request.session['current_lesson'] = lesson.id
            request.session['current_lesson_todo'] = self._get_default_lesson_order()
            request.session['tutor_mode'] = lesson.tutor_mode

        return lesson

    def _start_lesson(self, series) -> Lesson:
        """Starts a new lesson in the given series for the current user."""
        profile_series_level, _ = ProfileSeriesLevel.objects.get_or_create(user=self.learner, series=series, defaults={"level": 0})
        current_level = profile_series_level.level
        lesson = Lesson.objects.filter(series=series).order_by("lesson_id")[current_level]
        return lesson

    @staticmethod
    def _get_default_lesson_order() -> List[str]:
        """Returns the default lesson order."""
        return ['START', 'R', 'GS', 'V', 'WRAPUP']

    def _get_next_step(self, request, lesson) -> Tuple[str, Task]:
        request.session.modified = True
        next_type = request.session['current_lesson_todo'][0]
        task = None

        if self._requires_task(next_type):
            next_type, task = self._select_task(lesson, next_type, request)

        return next_type, task

    @staticmethod
    def _requires_task(next_type: str) -> bool:
        """Returns a boolean indicator whether the next step type requires a task or not."""
        return next_type not in {'START', 'WRAPUP'}

    def _select_task(self, lesson, next_type, request) -> Tuple[str, Task]:
        """Selects the next task randomly."""
        tasks = Task.objects.filter(lesson=lesson, type=next_type)
        cnt = tasks.count()
        if cnt == 0:
            # if we don't have such a task, remove it
            request.session['current_lesson_todo'].pop(0)
            next_type, task = self._get_next_step(request, lesson)
        else:
            task = tasks[random.randint(0, cnt-1)]
        return next_type, task
