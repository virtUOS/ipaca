from learning_environment.its.base import Json5ParseException
from django.conf import settings

class ShortTask():
    """A short answer task."""

    template = 'learning_environment/partials/short.html'

    @classmethod
    def check_json5(cls, task_json5, task_num=0):
        if "answer" not in task_json5:
            raise Json5ParseException(
                'Field "answer" is missing for short answer task task (task {})'.format(task_num))

    @classmethod
    def get_content_from_json5(cls, task_json5, task_num=0):
        return task_json5['answer']

    def __init__(self, task):
        self.task = task

    def analyze_solution(self, solution):
        context = {}
        analysis = {}

        is_cheating = (settings.CHEAT and 'CHEAT' in solution)

        if is_cheating:
            given_answer = self.task.content
        else:  # not cheating, full analysis
            given_answer = solution.get('answer', None)

        if self.task.content == given_answer:
            analysis['solved'] = True
        else:
            analysis['solved'] = False

# Levenshtein Distance
# Question: "Tim has drawn a picture."
# answer: "The picture !was! !drawn! by Tim."

# Short Answer Grading
        context['feedback'] = "hallo"
        context['mode'] = "result"  # display to try again
        return (analysis, context)

