"""
Pretest Class -neu
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
        # 1. check if a lesson has been started yet, if not, start lesson A
        # pick a lesson
        current_lesson_id = request.session.get('current_lesson', None) # Is a lesson started already?

        if current_lesson_id:
            try:
                lesson = Lesson.objects.get(lesson_id=current_lesson_id)
            except Lesson.DoesNotExist:
                raise Exception("Lesson from session does not exist: {}!".format(current_lesson_id))
        else:
            lesson = Lesson.objects.get(lesson_id="level-A", series="Adaptive Pretest")
            request.session['current_lesson'] = lesson.lesson_id
            request.session['done'] = 0 # NEW Counts completed tasks
            request.session['current_lesson_correct'] = 0 # counts how many tasks have been solved correctly
            request.session['tasks'] = None
            request.session.modified = True

        # 2. wenn eine Lesson beendet wird, nächste lesson starten
        # 2. when a lesson ends, start next lesson
        next_type = None
        num_tasks = Task.objects.filter(lesson=lesson).count() # num of tasks in level
        print(request.session['current_lesson'], request.session['current_lesson_correct'], request.session['done'], num_tasks)
        if request.session['current_lesson_correct'] / num_tasks > 2/3:
            if request.session['current_lesson'] == "level-A":
                next_level = "level-B"
            elif request.session['current_lesson'] == "level-B":
                next_level= "level-C" 
            elif request.session['current_lesson'] == "level-C":
                next_type = 'WRAPUP'
            if next_type != 'WRAPUP':
                lesson = Lesson.objects.get(lesson_id=next_level, series="Adaptive Pretest") # problem
                request.session['current_lesson'] = lesson.lesson_id
                request.session['tasks'] = None
                request.session['current_lesson_correct'] = 0 # counts how many tasks hav been solved correctly, set back to zero for the new level
                request.session.modified = True
        elif request.session['tasks'] == []:# NEW If 100% of all level tasks have been completed WrapUp
            next_type = 'WRAPUP'

        
        # 3. in einer lesson, nächste Aufgabe presentieren 
        # 3. in a lesson, present the next task
        # pick a task
        request.session.modified = True
        #next_type = "R"
        tasks = request.session.get("tasks", None)
        if not tasks and next_type != 'WRAPUP':
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