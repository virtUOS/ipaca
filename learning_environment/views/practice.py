from django.contrib.auth.decorators import login_required
from django.http import HttpResponseServerError, HttpResponseBadRequest, HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from learning_environment.its.learnermodel import Learnermodel
from learning_environment.its.smart_tutormodel import SmartTutormodel
# from learning_environment.its.tutor import get_tutor
from learning_environment.its.tutormodel import NoTaskAvailableError, Tutormodel
from learning_environment.models import Task, ProfileSeriesLevel, Lesson


@login_required
def practice(request: HttpRequest) -> HttpResponse:
    """Display a task for practicing."""

    context = {'mode': 'solve'}

    # start a lesson
    if request.method == 'POST' and 'start' in request.POST:
        if 'current_lesson_todo' not in request.session:  # if there's no todo, we have a corrupt state -> show start screen
            return redirect('myhome')
        request.session['current_lesson_todo'].pop(0)  # remove the start item
        request.session.modified = True

        # pick a lesson
        current_lesson_id = request.session.get('current_lesson', None)
        if current_lesson_id:
            try:
                lesson = Lesson.objects.get(pk=current_lesson_id)
            except Lesson.DoesNotExist:
                raise Exception("Lesson from session does not exist: {}!".format(current_lesson_id))

        # tutor = get_tutor(lesson.tutor_mode, request.user)
        if lesson.tutor_mode is "S":
            tutor = SmartTutormodel(request.user)
        else:
            tutor = Tutormodel(request.user)

        try:
            (state, lesson, task) = tutor.next_task(request)
        except NoTaskAvailableError:
            return HttpResponseServerError("Error: No task available!")

        try:
            (state, lesson, task) = tutor.next_step(request)
        except NoTaskAvailableError:
            return HttpResponseServerError("Error: No task available!")
        context['state'] = state

    # finish a lesson
    elif request.method == 'POST' and 'finish' in request.POST:
        if not 'current_lesson_todo' in request.session:  # if there's no todo, we have a corrupt state -> show start screen
            # TODO: message
            return redirect('myhome')
        if request.session['current_lesson_todo'][0] != 'WRAPUP':  # if we didn't finish a lesson, we have corrupt state
            # TODO: message
            return redirect('myhome')

        # increase level for current series
        current_lesson_series = request.session.get('lesson_series', 'General')
        try:
            psl = ProfileSeriesLevel.objects.get(user=request.user, series=current_lesson_series)
            psl.level += 1
            psl.save()
        except ProfileSeriesLevel.DoesNotExist:
            ProfileSeriesLevel.objects.create(user=request.user, series=current_lesson_series, level=1)

        return redirect('myhome')

    # analyze a solution
    elif request.method == 'POST':
        try:
            task = Task.objects.get(pk=int(request.POST['task']))
        except (KeyError, Task.DoesNotExist):
            return HttpResponseBadRequest("Invalid Task ID")
        # Evaluate solution
        learnermodel = Learnermodel(request.user)
        analysis, learnermodel_context = learnermodel.update(task, request.POST)
        context.update(learnermodel_context)
        if analysis.get('solved', False):  # we solved a task, so we remove its type from the session todo list
            context['solved'] = True
            if 'current_lesson_todo' in request.session and len(request.session['current_lesson_todo']) > 0:
                request.session['current_lesson_todo'].pop(0)
            request.session.modified = True
        else:
            context['solved'] = False
        lesson = task.lesson
        context['state'] = context['mode']
    elif 'redo' in request.GET:  # show a task again
        try:
            task = Task.objects.get(pk=int(request.GET['redo']))
        except KeyError:
            return HttpResponseBadRequest("Error: No such ID")
        lesson = task.lesson
        context['state'] = context['mode']
    else:  # fetch new task and show it
        # tutor = get_tutor(None, request.user)
        tutor = Tutormodel(request.user)
        try:
            (state, lesson, task) = tutor.next_step(request)
        except NoTaskAvailableError:
            return HttpResponseServerError("Error: No task available!")
        context['state'] = state

    context['task'] = task
    context['lesson'] = lesson
    # Pass all information to template and display page
    return render(request, 'learning_environment/task.html', context=context)
