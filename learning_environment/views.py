from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from .forms import *
from .its.learnermodel import Learnermodel
from .its.tutormodel import Tutormodel, NoTaskAvailableError
from .models import Lesson, Task, Solution, Profile, ProfileSeriesLevel
import plotly.graph_objects as go
from django.db.models import Sum,Count
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.graph_objects as px
import numpy as np
import matplotlib.pyplot as plt
import tkinter
import matplotlib
from matplotlib.pyplot import figure
import mpld3


class SignUpView(SuccessMessageMixin, generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
    success_message = "User was created successfully. You may now log in."

@login_required
def practice(request):
    """Display a task for practicing."""

    context = {'mode': 'solve'}

    # start a lesson
    if request.method == 'POST' and 'start' in request.POST:
        if not 'current_lesson_todo' in request.session:  # if there's no todo, we have a corrupt state -> show start screen
            return redirect('myhome')
        request.session['current_lesson_todo'].pop(0)  # remove the start item
        request.session.modified = True
        tutor = Tutormodel(request.user)
        try:
            (state, lesson, task) = tutor.next_task(request)
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
            request.session['current_lesson_todo'].pop(0)
            request.session.modified = True

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
        tutor = Tutormodel(request.user)
        try:
            (state, lesson, task) = tutor.next_task(request)
        except NoTaskAvailableError:
            return HttpResponseServerError("Error: No task available!")
        context['state'] = state

    context['task'] = task
    context['lesson'] = lesson
    # Pass all information to template and display page
    return render(request, 'learning_environment/task.html', context=context)


# basic view login NOT required
def home(request):
    page = 'home'  # for highlighting current page
    if request.user.is_authenticated:
        return redirect('myhome')
    return render(request, 'learning_environment/home.html', locals())


# basic view for authenticated users
def myhome(request):
    page = 'myhome'  # for highlighting current page
    try:
        request.user.save()
    except Profile.DoesNotExist:
        p = Profile(user=request.user)
        p.save()

    # delete chosen lesson from session
    try:
        del request.session['current_lesson']
    except KeyError:
        pass
    try:
        del request.session['current_lesson_todo']
    except KeyError:
        pass

    # Lesson series
    all_lesson_series = sorted([x['series'] for x in Lesson.objects.values('series').distinct()])

    # set series from GET parameter (if valid)
    if 'series' in request.GET:
        s = request.GET['series']
        if s in all_lesson_series:
            request.session['lesson_series'] = s

    try:
        series = request.session['lesson_series']
    except KeyError:
        request.session['lesson_series'] = 'General'
        series = 'General'

    # determine current level (and create if necessary)
    psl, created = ProfileSeriesLevel.objects.get_or_create(user=request.user, series=series)
    current_level = psl.level

    # pick all levels for chosen lesson series
    levels = Lesson.objects.filter(series = series).order_by('lesson_id')

    return render(request, 'learning_environment/myhome.html', locals())


class TaskListView(ListView):
    """List all tasks"""
    model = Task
    paginate_by = 25  # 25 entries max per page

    def get_ordering(self):
        ordering = self.request.GET.get('ordering', 'lesson__name')
        # validate ordering here
        return ordering


class LessonDetailView(DetailView):
    """Show details for a single lesson (esp. JSON5)"""
    model = Lesson

class LessonCreateView(FormView):

    def post(self, request):
        form = LessonCreationForm(request.POST)
        if form.is_valid():
            l = Lesson.create_from_json5(form.cleaned_data.get('json5'))
            messages.info(request, "Lesson {} successfully created.".format(l.lesson_id))
            return redirect('home')
        else:
            msg = form.errors
        return render(request, 'learning_environment/lesson_form.html', locals())
    def get(self, reguest):
        form = LessonCreationForm()
        return render(reguest, 'learning_environment/lesson_form.html', locals())

def learner_dashboard(request):
    """Prepare data for learner's own dashboard and show it."""
    solutions = Solution.objects.filter(user=request.user).order_by('timestamp')  # all solutions from current user
    num_tasks = solutions.count()  # how tasks did this user try
    correct_solutions = Solution.objects.filter(user=request.user, solved=True).count()  # how many of them were correct?
    if num_tasks > 0:  # calculate percentage of correct tasks (or 0 if no tasks)
        tasks_correctness = correct_solutions / num_tasks * 100.0
    else:
        tasks_correctness = 0.0

    return render(request, 'learning_environment/learner_dashboard.html', locals())  # pass all local variable to template

def solutions_chart(request):
    """Prepare data for learner's own dashboard and show it."""
    correct_solutions = Solution.objects.filter(user=request.user,solved=True).count()  # how many of them were correct?
    wrong_solutions = Solution.objects.filter(user=request.user, solved=False).count()
    fig = go.Figure(
        data=[go.Bar(x=["correct solutions", "wrong solutions"], y=[correct_solutions, wrong_solutions])],
        layout_title_text= str(request.user) + " Total correct/wrong solutions",

    )
    fig.show()

    return render(request, 'learning_environment/learner_dashboard.html', locals())  # pass all local variable to template

def progress_chart(request):
    """Prepare data for learner's own dashboard and show it."""
    progress = []
    tasks = []
    correct_counter = 0
    tasks_counter = 0
    solutions = Solution.objects.filter(user=request.user).order_by('timestamp')
    for sol in solutions:
        temp = 0.0
        tasks_counter +=1
        if sol.solved==True:
            correct_counter +=1
        temp = correct_counter/tasks_counter * 100.0
        progress.append(temp)
        tasks.append(tasks_counter)

    fig = go.Figure(go.Scatter(
        x=tasks,
        y=progress,
       ),
        layout_title_text=str(request.user) + " Progress Chart")

    fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=1,
            dtick=1
        )
    )

    fig.show()

    return render(request, 'learning_environment/learner_dashboard.html', locals())  # pass all local variable to template

def questions_chart(request):
    """Prepare data for learner's own dashboard and show it."""
    all_questions = Solution.objects.values('task_id').annotate(Count('task_id'))
    print("all questions: "+str(all_questions))
    correct_questions = Solution.objects.values('task_id').filter(solved=True).annotate(Count('solved'))
    print("correct_questions: "+str(correct_questions))
    wrong_questions = Solution.objects.values('task_id').filter(solved=False).annotate(Count('solved'))
    print("wrong_questions: " + str(wrong_questions))


    correct=[]
    wrong=[]
    all=[]

    for a in all_questions:
        task_id = a.get('task_id')
        print("task_id: " + str(task_id))
        all.append(task_id)
        exists_correct_questions = False;
        exists_wrong_questions = False;

        for c in correct_questions:
            if c.get('task_id') == task_id:
                correct_count = c.get('solved__count')
                print(str(task_id)+" correct_count: " + str(correct_count))
                correct.append(correct_count)
                exists_correct_questions = True;
                print(" exists_correct_questions: " + str(exists_correct_questions))
        if exists_correct_questions is False:
            correct.append(0)
            print("NOT exists_correct_questions: " + str(exists_correct_questions))

        for r in wrong_questions:
            if r.get('task_id') == task_id:
                wrong_count = r.get('solved__count')
                print(str(task_id)+" wrong_count: " + str(wrong_count))
                wrong.append(wrong_count)
                exists_wrong_questions = True;
                print(" exists_wrong_questions: " + str(exists_wrong_questions))
        if exists_wrong_questions is False:
            wrong.append(0)
            print("NOT exists_wrong_questions: " + str(exists_wrong_questions))

    print("all: "+str(all))
    print("correct_count: "+str(correct))
    print("wrong_count: "+str(wrong))

    fig = go.Figure(data=[go.Bar(
        name = 'Correct Solutions',
        x = all,
        y = correct
    ),
    go.Bar(
        name = 'Wrong Solutions',
        x = all,
        y = wrong
   )
    ],
        layout_title_text="Solutions Analysis Chart"
    )

    fig.update_layout(barmode='stack', xaxis=dict(
            tick0=1,
            dtick=1))
    fig.show()

    return render(request, 'learning_environment/learner_dashboard.html', locals())  # pass all local variable to template

def users_activity(request):
    return render(request, 'learning_environment/learner_dashboard.html', locals())

def global_dashboard(request):
    solutions = Solution.objects.all().order_by('timestamp')  # all solutions
    num_solutions = solutions.count()  # how tasks did this user try
    correct_solutions = Solution.objects.filter(solved=True).count()  # how many of them were correct?
    if num_solutions > 0:  # calculate percentage of correct tasks (or 0 if no tasks)
        tasks_correctness = correct_solutions / num_solutions * 100.0
    else:
        tasks_correctness = 0.0
    return render(request, 'learning_environment/global_dashboard.html', locals())  # pass all local variable to template


def learner_reset(request):
    if request.user.is_authenticated:
        current_lesson_series = request.session.get('lesson_series', 'General')
        try:
            psl = ProfileSeriesLevel.objects.get(user=request.user, series=current_lesson_series)
            psl.level = 0
            psl.save()
            messages.info(request, "Level for series {} has been reset for user {}".format(current_lesson_series, request.user.username))
        except ProfileSeriesLevel.DoesNotExist:
            pass
        return redirect("myhome")
    else:
        return redirect("home")
