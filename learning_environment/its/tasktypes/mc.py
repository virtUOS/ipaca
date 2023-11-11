from learning_environment.its.base import Json5ParseException
from django.conf import settings

class MCTask():
    """A multiple choice task."""

    template = 'learning_environment/partials/mc.html'

    def __init__(self, task):
        self.task = task

    def analyze_solution(self, solution):
        analysis = {'solved': True, 'solution':{} }
        context = {'mode': 'result'}

        is_cheating = (settings.CHEAT and 'CHEAT' in solution)

        for i in range(len(self.task.content)):  # check all choices from task
            if is_cheating:
                checked = self.task.content[i]['correct']
            else:
                checked = 'solution-{}-{}'.format(self.task.id, i) in solution  # a field was chosen?
            analysis['solution'][i] = checked  # save for later reference
            self.task.content[i]['checked'] = checked  # TODO: Find a proper solution, this is monkey patching...
            if checked != self.task.content[i]['correct']:
                analysis['solved'] = False

        return (analysis, context)

    @classmethod
    def check_json5(cls, task_json5, task_num=0):
        if "choices" not in task_json5:
            raise Json5ParseException(
                'Field "choices" is missing for multiple choice task (task {})'.format(task_num))
        choice_num = 0
        for c in task_json5["choices"]:
            choice_num += 1
            for choice_field in [("text", str, "a string"), ("correct", bool, "True or False"),
                                 ("feedback", str, "a string")]:
                if choice_field[0] not in c:
                    raise Json5ParseException(
                        'Field "{}" is missing for choice {} in task {}'.format(choice_field[0],
                                                                                              choice_num, task_num))
                if not isinstance(c[choice_field[0]], choice_field[1]):
                    raise Json5ParseException(
                        'Field "{}" for choice {} in task {} has wrong type, it has to be {}'.format(
                            choice_field[0], choice_num, task_num, choice_field[2]))
        return True

    @classmethod
    def get_content_from_json5(cls, task_json5, task_num=0):
        return task_json5['choices']
