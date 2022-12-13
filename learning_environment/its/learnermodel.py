"""ipaca Learner Model

The learner model maintains a model about a given learner's competencies.

"""

from .tasks import TaskTypeFactory
from learning_environment.models import Solution, Profile
from django_gamification.models import BadgeDefinition, Category

# indicate how many XP are needed for which level up
LEVEL_XP = {
    '1': 0,
    '2': 20,
    '3': 40,
    '4': 70,
    '5': 100,
    '6': 140,
    '7': 180,
    '8': 230,
    '9': 280,
    '10': 350,
}

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
        
        # award XP for correct solutions, and a few XP for wrong solutions
        # create message
        if analysis.get('solved', False):
            # Update user XP
            currentUser = Profile.objects.get(user=self.learner)
            currentUser.total_XP += 10
            # check if user has achieved enough XP for a level up
            # NOT WORKING YET
            try:
                if currentUser.total_XP >= LEVEL_XP[currentUser.gamification_level] and currentUser.gamification_level < 10:
                    currentUser.gamification_level += 1
            except:
                pass
            currentUser.save()
            # Provide user feedback
            context['msg'] = "Congratulation! That's correct!"
        else:
            currentUser = Profile.objects.get(user=self.learner)
            currentUser.total_XP += 3
            try:
                if currentUser.total_XP >= LEVEL_XP[currentUser.gamification_level] and currentUser.gamification_level < 10:
                    currentUser.gamification_level += 1
            except:
                pass
            currentUser.save()
            # provide user feedback
            context['msg'] = "Oh no, that's not correct."
        return analysis, context
