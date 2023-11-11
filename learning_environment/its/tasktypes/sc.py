from learning_environment.its.base import Json5ParseException
from django.conf import settings

class SCTask():
    """A single choice task."""

    template = 'learning_environment/partials/sc.html'

    @classmethod
    def check_json5(cls, task_json5, task_num=0):
        if "choices" not in task_json5:
            raise Json5ParseException(
                'Field "choices" is missing for single/multiple choice task (task {})'.format(task_num))
        choice_num = 0
        correct_choices = 0
        for c in task_json5["choices"]:
            choice_num += 1
            for choice_field in [("text", str, "a string"), ("correct", bool, "True or False"), ("feedback", str, "a string")]:
                if choice_field[0] not in c:
                    raise Json5ParseException(
                        'Field "{}" is missing for choice {} in task {}'.format(choice_field[0], choice_num, task_num))
                if not isinstance(c[choice_field[0]], choice_field[1]):
                    raise Exception('Field "{}" for choice {} in task {} has wrong type, it has to be {}'.format(
                        choice_field[0], choice_num, task_num, choice_field[2]))
            if c['correct']:
                correct_choices += 1
        if correct_choices != 1:
            raise Json5ParseException(
                "Task {} has {} choices marked as correct, but you need exactly 1.".format(task_num, correct_choices))
    @classmethod
    def get_content_from_json5(cls, task_json5, task_num=0):
        return task_json5['choices']

    def __init__(self, task):
        self.task = task

    def analyze_solution(self, solution):
        context = {}
        analysis = {}

        is_cheating = (settings.CHEAT and 'CHEAT' in solution)

        if is_cheating:
            for i in range(len(self.task.content)):
                if self.task.content[i]['correct']:
                    chosen = i
                    break
        else:  # not cheating, full analysis
            chosen = int(solution.get('solution-{}'.format(self.task.id), -1))

        analysis['solution'] = chosen
        context['chosen'] = chosen
        if chosen == -1:
            context['mode'] = "solve"  # display to try again
        else:
            counter = 0
            correct = -1
            for choice in self.task.content:
                if choice['correct']:
                    correct = counter
                counter += 1
            if correct == -1:
                raise Exception("Invalid task {}: No correct answer in data".format(self.task.id))
            if chosen == correct:  # correct solution
                analysis['solved'] = True
            else:
                analysis['solved'] = False
            context['mode'] = 'result'  # show result and feedback
            context['show_feedback'] = chosen

        return (analysis, context)
