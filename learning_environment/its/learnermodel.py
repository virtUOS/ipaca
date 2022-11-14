"""ipaca Learner Model

The learner model maintains a model about a given learner's competencies.

"""

from .tasks import TaskTypeFactory
from learning_environment.models import Solution

class Learnermodel:

    def __init__(self, learner):
        """Initializes the learner model for a given learner.

        learner: User object"""

        self.learner = learner

    def update(self, task, solution):
        """Updates the learner model by analyzing the solution for a task.

        task: Task object
        solution: Dictionary with solution (usually form data from POST request)

        Return a tuple of analysis dictionary and context dictionary"""

        analyzer = TaskTypeFactory.getObject(task)
        (analysis, context) = analyzer.analyze_solution(solution)

        # Save solution and analysis to database
        solution = Solution(user=self.learner, task=task, solved=analysis.get('solved', False), analysis=analysis)
        solution.save()

        # create message
        if analysis.get('solved', False):
            context['msg'] = "Congratulation! That's correct!"
        else:
            context['msg'] = "Oh no, that's not correct."
        return analysis, context
        