"""ipaca Tutor Model

The tutor model is able to determine appropriate actions for a given learner. (E.g. generate a 'next task')

"""

import random
from learning_environment.models import Lesson, Task, ProfileSeriesLevel


class NoTaskAvailableError(Exception):
    pass


class TutormodelPretest:

    def __init__(self, learner):
        """Initializes the tutor model for a given learner.
        learner: User object"""
        self.learner = learner

    def next_task(self, request):
        """Pick a next task for the learner.
        Returns tuple:
        (STATE, lesson, task)
        """

        # 1. gucken, ob noch keine lesson gestartet wurde, dann lesson A
        # pick a lesson
        current_lesson_id = request.session.get('current_lesson', None) #schon in einem level?

        if current_lesson_id:
            try:
                lesson = Lesson.objects.get(pk=current_lesson_id)
            except Lesson.DoesNotExist:
                raise Exception("Lesson from session does not exist: {}!".format(current_lesson_id))
        else:
            lesson = Lesson.objects.get(lesson_id="level-A", series="Adaptive Pretest")
            request.session['current_lesson'] = lesson.id
            request.session['done'] = 0 # NEW Zählt erledigte Aufgaben
            request.session['current_lesson_correct'] = 0 # zählt wie viele Aufgaben korrekt gelöst wurden
            request.session['tasks'] = None
            request.session.modified = True

        # 2. wenn eine Lesson beendet wird, nächste lesson starten
        num_tasks = Task.objects.filter(lesson=lesson).count() # num of tasks in level
        if request.session['done'] / num_tasks == 1:# NEW
            next_type = 'WRAPUP'
        if request.session['current_lesson_correct'] / num_tasks > 2/3:
            if request.session['current_lesson'] == "level-A":
                next_level = "level-B"
            elif lesson.id == "level-B":
                next_level = "level-C" #TODO was passiert nach level C?
            elif lesson.id == "level-C":
                next_type = 'WRAPUP'
            lesson = Lesson.objects.get(lesson_id=next_level, series="Adaptive Pretest") # problem
            request.session['current_lesson'] = lesson.id
            request.session['current_lesson_correct'] = 0 # zählt wie viele Aufgaben korrekt gelöst wurden
            request.session.modified = True

        
        # 3. in einer lesson, nächste Aufgabe presentieren 
        # pick a task
        request.session.modified = True
        next_type = "R"
        tasks = request.session.get("tasks", None)
        if not tasks:
            next_type = "START" 
            tasks = list(Task.objects.filter(lesson=lesson).values_list('id', flat=True))  # get list of task ids (we need ids becuse we cannot store a queryset in the session)
            request.session['tasks'] = tasks
        if next_type == 'START': # Start- und Endseite anzeigen
            return next_type, lesson, None
        elif next_type == 'WRAPUP':
            return next_type, lesson, None
        else:  # pick random task of fitting type
            task = Task.objects.get(pk=tasks.pop(random.randrange(len(tasks))))  # pick and remove a random task id from list, fetch Task object from database
            request.session.modified = True
            return "R", lesson, task #message at the end -> task.html

       # return "Your current level is: " lesson.id #NEW