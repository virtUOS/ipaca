from learning_environment.its.base import Json5ParseException

# https://code-boxx.com/drag-drop-sortable-list-javascript/

class SortParTask():
    """A sortable paragraph task."""

    template = 'learning_environment/partials/sortpar.html'

    def __init__(self, task):
        self.task = task

    def analyze_solution(self, solution):
        analysis = {'solved': True, 'solution':{} }
        context = {'mode': 'result'}

        # TODO: check if sorting is correct

        return (analysis, context)

    @classmethod
    def check_json5(cls, task_json5, task_num=0):
        # TODO: check if json5 is correct
        return True

    @classmethod
    def get_content_from_json5(cls, task_json5, task_num=0):
        return task_json5['choices']
