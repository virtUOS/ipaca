from typing import Tuple, List, Dict, Any

from django.db.models import Count

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
            user_levels = self._get_user_levels()

            current_user_level = 0
            for ind, user in enumerate(user_levels):
                if user["id"] == self.learner.id:
                    current_user_level = ind / len(user_levels)
                    break

            # select task id accordingly to skill of user and estimated task difficulty
            index = int((1 - current_user_level) * len(task_difficulties) - 1)
            task_id = task_difficulties[index]["id"]
            task = Task.objects.get(pk=task_id)

        return next_type, task

    @staticmethod
    def _get_task_difficulties(lesson, next_type) -> List[Dict[str, Any]]:
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
    def _get_user_levels():
        query_set = Solution.objects.values('user', 'solved').annotate(count=Count('id')).order_by('user', 'solved')
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
