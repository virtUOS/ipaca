"""
View elements for the practice phase.
"""
from typing import Dict

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from learning_environment.its.learnermodel import Learnermodel
from learning_environment.its.tutor import get_tutor_model
from learning_environment.models import Task, ProfileSeriesLevel


@login_required
def practice(request: HttpRequest) -> HttpResponse:
    """Display a task for practicing."""
    redirect_or_error_response = None
    context = {'mode': 'solve'}

    # start the lesson
    if request.method == 'POST' and 'start' in request.POST:
        redirect_or_error_response = _start_lesson(request, context)

    # finish a lesson
    elif request.method == 'POST' and 'finish' in request.POST:
        redirect_or_error_response = _finish_lesson(request)

    # analyze a solution
    elif request.method == 'POST':
        redirect_or_error_response = _analyze_solution(request, context)

    # show the current task again
    elif 'redo' in request.GET:
        _redo_task(context, task_id=int(request.GET['redo']))

    else:
        _get_task(request, context)

    # Pass all information to template and display page
    return render(request, 'learning_environment/task.html', context=context) if redirect_or_error_response is None else redirect_or_error_response


def _start_lesson(request: HttpRequest, context: Dict):
    """Starts a new lesson. It removes the 'START' item from the todo list and gets the first task."""
    if 'current_lesson_todo' not in request.session:  # if there's no todo, we have a corrupt state -> show start screen
        return redirect('myhome')

    # remove the start item
    request.session['current_lesson_todo'].pop(0)
    request.session.modified = True

    # get first task
    _get_task(request, context)


def _get_task(request: HttpRequest, context: Dict):
    """Gets the next task and stores it in context."""
    tutor = get_tutor_model(request.session.get('tutor_mode', ''), request.user)
    (state, lesson, task) = tutor.next_step(request)
    context['state'] = state
    context['task'] = task
    context['lesson'] = lesson


def _finish_lesson(request: HttpRequest):
    """Finishes a lesson."""
    if 'current_lesson_todo' not in request.session:  # if there's no todo, we have a corrupt state -> show start screen
        # TODO: message
        return redirect('myhome')
    if request.session['current_lesson_todo'][0] != 'WRAPUP':  # if we didn't finish a lesson, we have corrupt state
        # TODO: message
        return redirect('myhome')

    # increase level for current series
    current_lesson_series = request.session.get('lesson_series', 'General')
    psl, _ = ProfileSeriesLevel.objects.get_or_create(user=request.user, series=current_lesson_series, defaults={"level": 0})
    psl.level += 1
    psl.save()

    return redirect('myhome')


def _analyze_solution(request: HttpRequest, context: Dict):
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
    context['task'] = task
    context['lesson'] = lesson


def _redo_task(context: Dict, task_id: int):
    task = Task.objects.get(pk=task_id)
    lesson = task.lesson

    context['state'] = context['mode']
    context['task'] = task
    context['lesson'] = lesson
