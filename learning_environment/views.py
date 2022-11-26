from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic import View
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *
from .models import Lesson, Task, Solution, Profile, ProfileSeriesLevel
from .its.tutormodel import Tutormodel, NoTaskAvailableError
from .its.learnermodel import Learnermodel
import json
import time
import datetime
from itertools import groupby
from operator import itemgetter
from .anychart import *

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


class LessonCreateView(LoginRequiredMixin, FormView):

    def post(self, request):
        form = LessonCreationForm(request.POST)
        if form.is_valid():
            l = Lesson.create_from_json5(form.cleaned_data.get('json5'))
            messages.info(request, "Lesson {} successfully created.".format(l.lesson_id))
            return redirect('home')
        else:
            msg = form.errors
        return render(request, 'learning_environment/lesson_form.html', locals())
    def get(self, request):
        form = LessonCreationForm()
        return render(request, 'learning_environment/lesson_form.html', locals())


class LessonDeleteView(LoginRequiredMixin, View):

    def get(self, request, pk):
        try:
            l = Lesson.objects.get(pk=pk)
            name = l.lesson_id
            l.delete()
            messages.info(request, "Lesson {} successfully deleted.".format(name))
        except Lesson.DoesNotExist:
            messages.error(request, "Lesson {} not found.".format(pk))
            pass
        return redirect('tasklist')


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

def global_dashboard(request):
    solutions = Solution.objects.all().order_by('timestamp')  # all solutions
    num_solutions = solutions.count()  # how tasks did this user try
    correct_solutions = Solution.objects.filter(solved=True).count()  # how many of them were correct?
    if num_solutions > 0:  # calculate percentage of correct tasks (or 0 if no tasks)
        tasks_correctness = correct_solutions / num_solutions * 100.0
    else:
        tasks_correctness = 0.0

    # Extract only the timestamp/solved values and convert to list
    solutions_data = list(solutions.values('timestamp', 'solved'))
    
    # random data generation (delete_later)
    for i in range(1500):
        import random
        import datetime
        start = datetime.datetime.strptime('1/1/2020 1:30 PM', '%m/%d/%Y %I:%M %p')
        end = datetime.datetime.strptime('1/1/2023 4:50 AM', '%m/%d/%Y %I:%M %p')
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = random.randrange(int_delta)
        randDate = start + datetime.timedelta(seconds=random_second)
        randSolved = bool(random.getrandbits(1))
        data_entry = {"timestamp": randDate, "solved": randSolved}
        solutions_data.append(data_entry)
    
    # Group data by days and count the correct/incorrect solutions
    grouped_data = {}
    for data in solutions_data:
        # Convert datetime to YEAR-MONTH-DAY string
        day_string = data["timestamp"].strftime("%Y-%m-%d")
        data["timestamp"] = day_string

        # Init dictionary if not already present
        if day_string not in grouped_data: 
            grouped_data[day_string] = {'num_correct': 0, 'num_incorrect': 0}

        # Count correct/incorrect solutions 
        if data['solved']:
            grouped_data[day_string]["num_correct"] += 1
        else:
            grouped_data[day_string]["num_incorrect"] += 1

    # Reorder the grouped data by correct/incorrect for anychart graph
    correct_solutions_data = []
    incorrect_solutions_data = []
    for timestamp_day in grouped_data:
        correct_entry = {}
        correct_entry["x"] = timestamp_day  
        correct_entry["value"] = grouped_data[timestamp_day]["num_correct"]
        correct_solutions_data.append(correct_entry)

        incorrect_entry = {}
        incorrect_entry["x"] = timestamp_day
        incorrect_entry["value"] = grouped_data[timestamp_day]["num_incorrect"]
        incorrect_solutions_data.append(incorrect_entry)

    # Create series for column graph
    correct_series = {
        "name": "Correct",
        "enabled": True,
        "seriesType": "column",
        "clip": True,
        "isVertical": False,
        "xMode": "ordinal",
        "xScale": 0,
        "yScale": 1,
        "data": correct_solutions_data
    }
    incorrect_series= {
        "name": "Incorrect",
        "enabled": True,
        "seriesType": "column",
        "clip": True,
        "isVertical": False,
        "xMode": "ordinal",
        "xScale": 0,
        "yScale": 1,
        "data": incorrect_solutions_data
    }

    # Create JSON chart config
    chart = createBarChartConfig("solutions_bar_chart_container", [correct_series, incorrect_series])


    # Extract only the timestamp/solved values and convert to list
    category_data = list(solutions.values('timestamp', 'task'))

    print(Task.objects.filter(id=49).values('type'))
    
    
    # random data generation (delete_later)
    for i in range(1500):
        import random
        import datetime
        start = datetime.datetime.strptime('1/1/2020 1:30 PM', '%m/%d/%Y %I:%M %p')
        end = datetime.datetime.strptime('1/1/2023 4:50 AM', '%m/%d/%Y %I:%M %p')
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = random.randrange(int_delta)
        randDate = start + datetime.timedelta(seconds=random_second)
        randTask = random.randint(1, 70)
        data_entry = {"timestamp": randDate, "task": randTask}
        category_data.append(data_entry)
    
    # Group data by days and count the categories
    grouped_data = {}
    for data in category_data:
        # Convert datetime to YEAR-MONTH-DAY string
        day_string = data["timestamp"].strftime("%Y-%m-%d")
        data["timestamp"] = day_string

        # Init dictionary if not already present
        if day_string not in grouped_data: 
            grouped_data[day_string] = {'Reading': 0, 'Grammar': 0, 'Vocabulary': 0}

        # Get Task type
        task_type = list(Task.objects.filter(id=data["task"]).values('type'))[0]["type"]

        # Count correct/incorrect solutions 
        if task_type == 'R':
            grouped_data[day_string]["Reading"] += 1
        elif task_type == 'GS':
            grouped_data[day_string]["Grammar"] += 1
        elif task_type == 'V':
            grouped_data[day_string]["Vocabulary"] += 1

    # Reorder the grouped data by categories for anychart graph
    reading_data = ["Reading", 0]
    grammar_data = ["Grammar", 0]
    vocabulary_data = ["Vocabulary", 0]
    newest_reading_data = ["Reading", 0]
    newest_grammar_data = ["Grammar", 0]
    newest_vocabulary_data = ["Vocabulary", 0]

    today = datetime.datetime.today()
    last_week_day = today - datetime.timedelta(days=7)
    print(today)
    print(last_week_day) 
    for timestamp_day in grouped_data:

        reading_data[1] += grouped_data[timestamp_day]["Reading"]
        grammar_data[1] += grouped_data[timestamp_day]["Grammar"]
        vocabulary_data[1] += grouped_data[timestamp_day]["Vocabulary"]

        data_date = datetime.datetime.strptime(timestamp_day, "%Y-%m-%d").date()
        last_week_date = last_week_day.date()        
        is_older_than_a_week = last_week_date > data_date

        print("data_date: ", data_date)
        print("last_week_date: ", last_week_date)
        print("is_older_than_a_week: ", is_older_than_a_week)

        if not is_older_than_a_week:
            newest_reading_data[1] += grouped_data[timestamp_day]["Reading"]
            newest_grammar_data[1] += grouped_data[timestamp_day]["Grammar"]
            newest_vocabulary_data[1] += grouped_data[timestamp_day]["Vocabulary"]
    
    allPieData = [reading_data, grammar_data, vocabulary_data]
    newestPieData = [newest_reading_data, newest_grammar_data, newest_vocabulary_data]
    allPieChart = createDonutChartConfig("All Categories", "all_category_pie_chart_container", allPieData)
    newestPieChart = createDonutChartConfig("Last Week Categories", "newest_category_pie_chart_container", newestPieData)
    context = {
        "solutionsBarChartData": json.dumps(chart),
        "allCategoryPieChartData": json.dumps(allPieChart),
        "newestCategoryPieChartData": json.dumps(newestPieChart),
        "solutions": solutions, 
        "num_solutions": num_solutions,
        "correct_solutions": correct_solutions,
        "tasks_correctness": tasks_correctness
    }

    return render(request, 'learning_environment/global_dashboard.html', context)


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
