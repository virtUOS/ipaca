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
            lesson = Lesson.object.get(id="level-A", series="Adaptive Pretest")
            request.session['current_lesson'] = lesson.id
            request.session['done'] = 0 # NEW Zählt erledigte Aufgaben
            request.session['current_lesson_correct'] = 0 # zählt wie viele Aufgaben korrekt gelöst wurden
            request.session.modified = True

        # 2. wenn eine Lesson beendet wird, nächste lesson starten
        num_tasks = Task.objects.filter(lesson=lesson).count() # num of tasks in level
        if request.session['done'] / num_tasks == 1:# NEW
            complete = True
        if request.session['current_lesson_correct'] / num_tasks > 2/3:
            if lesson.id == "level-A":
                next_level = "level-B"
            elif lesson.id == "level-B":
                next_level = "level-C" #TODO was passiert nach level C?
            elif lesson.id == "level-C":
                complete = True #NEW
            lesson = Lesson.object.get(id=next_level, series="Adaptive Pretest")
            request.session['current_lesson'] = lesson.id
            request.session['current_lesson_correct'] = 0 # zählt wie viele Aufgaben korrekt gelöst wurden
            request.session.modified = True

        
        # 3. in einer lesson, nächste Aufgabe presentieren 
        # pick a task
        while complete == False: # NEW
            request.session.modified = True
            #if next_type == 'START': # Start- und Endseite anzeigen
             #   return next_type, lesson, None
            #elif next_type == 'WRAPUP':
             #   return next_type, lesson, None
            #else:  # pick random task of fitting type
            tasks = Task.objects.filter(lesson=lesson)
            cnt = tasks.count()
            tasks[r].remove() # NEW
            r = random.randint(0, cnt-1) # NEW Sonst mit if und ner 2. Liste
            task = tasks[r] # TODO random Aufgabe wählen, vorher bearbeitete Aufgaben rausnehmen
            return "R", lesson, task

        return "Your current level is: " lesson.id #NEW