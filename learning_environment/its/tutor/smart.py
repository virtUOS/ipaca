import random
from typing import Tuple, List, Dict, Any

from datetime import timedelta
from django.db.models import Count
from django.utils.timezone import localtime

from learning_environment.its.tutor import BaseTutorModel
from learning_environment.models import Task, Solution


class SmartTutorModel(BaseTutorModel):
    """
    The smart tutor uses information about the users performance and the performance of all other users of a task to get the next task.
    """

    def _select_task(self, lesson, next_type, request) -> Tuple[str, Task]:
        task = None
        task_difficulties = self._get_task_difficulties(lesson, next_type)

        if len(task_difficulties) == 0:
            # if we don't have such a task, remove it
            request.session['current_lesson_todo'].pop(0)
            next_type, task = self._get_next_step(request, lesson)
        else:
            user_levels = self._get_user_levels(next_type)

            # get the position of the user in all user levels as a probability
            current_user_level = 0
            for ind, user in enumerate(user_levels):
                if user["id"] == self.learner.id:
                    current_user_level = ind / len(user_levels)
                    break

            # select task id accordingly to skill of user and estimated task difficulty
            index = int((1 - current_user_level) * len(task_difficulties) - 1)
            task_id = task_difficulties[index]["id"]

            # check whether the task should repeated otherwise choose the next task
            remaining_tasks = len(task_difficulties)
            while not self._should_task_be_repeated(task_id, request.user):
                index = (index + 1) % len(task_difficulties)
                task_id = task_difficulties[index]["id"]
                remaining_tasks -= 1

                if remaining_tasks <= 0:
                    # it is very likely that all tasks have been completed recently
                    break

            task = Task.objects.get(pk=task_id)

        return next_type, task

    @staticmethod
    def _get_task_difficulties(lesson, next_type) -> List[Dict[str, Any]]:
        """
        Calculates the difficulty of each task of a specific type in a lesson. Therefore it is checked how often each
        task has been done and how often the answer was correct to calculate the share of correct answers. The tasks
        are then sorted by the share of correct answers and then returned.
        Example: [{'id':4, 'share':0.1}, {'id':3, 'share':0.4}, ..., {'id':5, 'share':0.7}]
        """
        tasks = Task.objects.filter(lesson=lesson, type=next_type)
        task_difficulties = []

        for task in tasks:
            all_task_solutions = Solution.objects.filter(task=task)
            all_task_solutions_count = all_task_solutions.count()
            correct_task_solutions = all_task_solutions.filter(solved=True)
            correct_task_solutions_count = correct_task_solutions.count()

            share = correct_task_solutions_count / all_task_solutions_count if all_task_solutions_count > 0 else 0
            task_difficulties.append({"id": task.id, "share": share})

        task_difficulties = sorted(task_difficulties, key=lambda x: x["share"])
        return task_difficulties

    @staticmethod
    def _should_task_be_repeated(task_id: str, user_id: str) -> bool:
        """
        Checks whether the given task should be repeated. The task is repeated if the last repetition was more than a
        week ago or if the probability of repetition is good. The probability increases with time.
        """
        try:
            last_solution = Solution.objects.filter(task=task_id, user=user_id).order_by('timestamp')[0]
        except IndexError:
            # the user has not yet done the task
            return True

        # calculate the probability to repeat the task
        one_week_delta = timedelta(weeks=1)
        last_solution_timestamp = last_solution.timestamp
        comparing_timestamp = localtime() - one_week_delta
        repeat_task_probability = (last_solution_timestamp - comparing_timestamp) / one_week_delta

        return random.random() < repeat_task_probability

    @staticmethod
    def _get_user_levels(task_type: str) -> List[Dict[str, Any]]:
        """
        Calculates all user levels for a given task type. Therefore it checks how each user has performed in tasks with
        the given task typ and calculates the correct share. The users are then sorted by this share and afterwards
        returned.
        Example: [{'id':8, 'share':0.51}, {'id':1, 'share':0.54}, ..., {'id':10, 'share':0.8}]
        """
        query_set = Solution.objects.values('user', 'solved').filter(task__type=task_type).annotate(count=Count('id')).order_by('user', 'solved')
        levels = []

        correct_answers = 0
        wrong_answers = 0
        current_user = None

        for result in query_set:
            if result['user'] != current_user:
                # safe the levels
                if current_user is not None:
                    all_answers = correct_answers + wrong_answers
                    share = correct_answers / all_answers
                    levels.append({"id": current_user, "share": share})

                # prepare for next user
                current_user = result['user']
                correct_answers = 0
                wrong_answers = 0

            if result['solved']:
                correct_answers = result['count']
            else:
                wrong_answers = result['count']

        # save the last user's data
        if current_user is not None:
            all_answers = correct_answers + wrong_answers
            share = correct_answers / all_answers
            levels.append({"id": current_user, "share": share})

        levels = sorted(levels, key=lambda x: x["share"])

        return levels
