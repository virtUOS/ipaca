"""ipaca Learner Model

The learner model maintains a model about a given learner's competencies.

"""

from .tasks import TaskTypeFactory
from learning_environment.models import Solution, Profile
import datetime
from datetime import timedelta, date

# indicate how many XP are needed for which level up
LEVEL_XP = {
    '1': 20,
    '2': 40,
    '3': 70,
    '4': 100,
    '5': 140,
    '6': 180,
    '7': 230,
    '8': 280,
    '9': 350,
}

today = datetime.date.today()

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
        # add global variables
        global LEVEL_XP
        global today

        # Save solution and analysis to database
        solution = Solution(user=self.learner, task=task, solved=analysis.get('solved', False), analysis=analysis)
        solution.save()
        # award XP for correct solutions, and a few XP for wrong solutions
        if analysis.get('solved', False):
            # award user XP
            currentUser = Profile.objects.get(user=self.learner)
            currentUser.total_XP += 10

            # check if the last solution was handed in yesterday, if yes increase the daily streak counter by 1
            # if no, set the last active time to now and reset the daily streak to 1

            if currentUser.last_active + timedelta(days=1) == today:
                currentUser.last_active = datetime.date.today()
                currentUser.streak_counter += 1
            else:
                currentUser.last_active = datetime.date.today()
                currentUser.streak_counter = 1 
            # check if user has enough XP to level up
            if currentUser.gamification_level < 10 and currentUser.total_XP >= LEVEL_XP[str(currentUser.gamification_level)]:
                # raise gamification level
                currentUser.gamification_level += 1
            # save current stats to user 
            currentUser.save()
            # Provide user feedback
            context['msg'] = "Congratulation! That's correct!"
        else:
            currentUser = Profile.objects.get(user=self.learner)
            currentUser.total_XP += 3
            
            if currentUser.last_active + timedelta(days=1) == today:
                currentUser.last_active = datetime.date.today()
                currentUser.streak_counter += 1
            else:
                currentUser.last_active = datetime.date.today()
                currentUser.streak_counter = 1 
            #if datetime.date.today() - currentUser.last_active > timedelta(days=1) and datetime.date.today() - currentUser.last_active < timedelta(days=0):
                #currentUser.last_active = datetime.date.today()
                #currentUser.streak_counter = 1

            #else:
                #currentUser.last_active = datetime.date.today()
                #currentUser.streak_counter += 1

            # check if user has enough XP to level up
            if currentUser.gamification_level < 10 and currentUser.total_XP >= LEVEL_XP[str(currentUser.gamification_level)]:
                # raise gamification level
                currentUser.gamification_level += 1
            # save current stats to user 
            currentUser.save()
            # provide user feedback
            context['msg'] = "Oh no, that's not correct."
        return analysis, context