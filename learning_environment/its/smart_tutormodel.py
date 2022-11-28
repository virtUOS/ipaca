"""ipaca Tutor Model

The tutor model is able to determine appropriate actions for a given learner. (E.g. generate a 'next task')

"""

import random
from learning_environment.models import Lesson, Task, ProfileSeriesLevel
import sqlite3


class NoTaskAvailableError(Exception):
    pass


class SmartTutormodel:

    def __init__(self, learner):
        """Initializes the tutor model for a given learner.
        learner: User object"""
        self.learner = learner

    def __get_tasks_level(self, connection, task_type, lesson):
        cur = connection.cursor()
        cur.execute(f"SELECT DISTINCT(id) FROM learning_environment_task \
            WHERE type = '{task_type}' AND lesson_id = {lesson}")
        # cur.execute(f'SELECT DISTINCT(s.task_id) FROM learning_environment_solution s \
        #     LEFT JOIN learning_environment_task t ON t.id = s.task_id \
        #     LEFT JOIN learning_environment_lesson l ON l.id = t.lesson_id \
        #     WHERE l.tutor_mode = "S"')
        rows = cur.fetchall()
        task_ids = [x[0] for x in rows]
        print("Rows", rows)
        difficulty = []
        for id in task_ids:
            cur.execute(f"SELECT solved FROM learning_environment_solution WHERE task_id = {id}")
            rows = cur.fetchall()
            correct = [x[0] for x in rows if x[0] == 1]
            if len(rows) == 0:
                share = 0
            else:
                share = len(correct) / len(rows)
            difficulty.append({"id": id, "share":share})
        difficulty = sorted(difficulty, key=lambda x: x["share"])
        return difficulty

    def __get_user_levels(self, connection):
        cur = connection.cursor()
        cur.execute(f"SELECT DISTINCT(user_id) FROM learning_environment_solution")
        rows = cur.fetchall()
        user_ids = [x[0] for x in rows]
        levels = []
        for id in user_ids:
            cur.execute(f"SELECT solved FROM learning_environment_solution level WHERE user_id = {id}")
            rows = cur.fetchall()
            correct = [x[0] for x in rows if x[0] == 1]
            share = len(correct) / len(rows)
            levels.append({"id": id, "share":share})
        levels = sorted(levels, key=lambda x: x["share"])
        return levels

    def next_task(self, request):
        """Pick a next task for the learner.
        Returns tuple:
        (STATE, lesson, task)
        """

        con = sqlite3.connect("db.sqlite3")

        order = ['START', 'R', 'R', 'GS', 'V', 'WRAPUP']

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
            task_difficulties = self.__get_tasks_level(con, next_type, current_lesson_id)
            user_levels = self.__get_user_levels(con)
            user_level = 0
            for ind, user in enumerate(user_levels):
                if user["id"] == self.learner.id:
                    user_level = ind / len(user_levels)

            task_id = task_difficulties[int((1 - user_level) * len(task_difficulties)) - 1]["id"]
            task = Task.objects.get(pk=task_id)
            return next_type, lesson, task

            # next_type = request.session['current_lesson_todo'][0]
            # request.session.modified = True
            # if next_type == 'START':
            #     return next_type, lesson, None
            # elif next_type == 'WRAPUP':
            #     return next_type, lesson, None
            # else:  # pick random task of fitting type
            #     tasks = Task.objects.filter(lesson=lesson, type=next_type)
            #     cnt = tasks.count()
            #     if cnt == 0:
            #         request.session['current_lesson_todo'].pop(0)  # if we don't have such a task, remove it
            #         continue  # next state
            #     task = tasks[random.randint(0, cnt-1)]
            #     return next_type, lesson, task

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
