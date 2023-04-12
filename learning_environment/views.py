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


class SignUpView(SuccessMessageMixin, generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
    success_message = "User was created successfully. You may now log in."

@login_required
def practice(request, startlesson=None):
    """Display a task for practicing."""

    context = {'mode': 'solve'}

    # start a lesson
    if 'review' in request.GET:
        context['review'] = True

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

    elif startlesson:
        try:
            lesson = Lesson.objects.get(pk=int(startlesson))
        except KeyError:
            return HttpResponseBadRequest("Error: No such Lesson")
        context['state'] = context['mode']

    else:  # fetch new task and show it

        start_new_lesson = None
        if 'lesson' in request.GET:  # explicitly start a specific lession by using the ?lesson=<id> parameter
            try:
                start_new_lesson = Lesson.objects.get(pk=int(request.GET['lesson']))
            except KeyError:
                return HttpResponseBadRequest("Error: No such Lesson")

        tutor = Tutormodel(request.user)
        try:
            # either continue with standard tutor model or explicitly start a specific lesson
            (state, lesson, task) = tutor.next_task(request, start_new_lesson)
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
    # psl, created = ProfileSeriesLevel.objects.get_or_create(user=request.user, series=series)
    # current_level = psl.level

    # pick all levels for chosen lesson series
    # levels = Lesson.objects.filter(series = series).order_by('lesson_id')
    # levels = Lesson.objects.filter(series = series).order_by('lesson_id')


    solutions = Solution.objects.filter(user=request.user).order_by('timestamp')  # all solutions from current user
    num_tasks = solutions.count()  # how tasks did this user try
    correct_solutions = Solution.objects.filter(user=request.user,
                                                solved=True).count()  # how many of them were correct?
    if num_tasks > 0:  # calculate percentage of correct tasks (or 0 if no tasks)
        tasks_correctness = round(correct_solutions / num_tasks * 100.0, 2)
    else:
        tasks_correctness = 0.0

    if Solution.objects.filter(user=request.user, solved=False).exists():
        wrong_solutions = Solution.objects.filter(user=request.user, solved=False)
        # get unique task id of wrong solutions
        wrong_solutions_unique = [x['task'] for x in wrong_solutions.values('task').distinct()]
        wrong_tasks = Task.objects.filter(id__in=wrong_solutions_unique)

    else:
        wrong_tasks = None
    id_lessons = [s.task.lesson.lesson_id for s in solutions]

    new_lessons = Lesson.objects.all().exclude(lesson_id__in=id_lessons).order_by('id')

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


def academic_series(request):
    psl, created = ProfileSeriesLevel.objects.get_or_create(user=request.user, series='Academic')
    current_level = psl.level
    lessons = Lesson.objects.filter(series='Academic English').order_by('lesson_id')
    paginate_by = 25  # 25 entries max per page

    return render(request, 'learning_environment/academic_series.html', locals())  # pass all local variable to template

def general_series(request):
    psl, created = ProfileSeriesLevel.objects.get_or_create(user=request.user, series='General')
    current_level = psl.level
    lessons = Lesson.objects.filter(series='General').order_by('lesson_id')
    paginate_by = 25  # 25 entries max per page
    return render(request, 'learning_environment/general_series.html', locals())  # pass all local variable to template

def learner_dashboard(request):
    """Prepare data for learner's own dashboard and show it."""
    solutions = Solution.objects.filter(user=request.user).order_by('timestamp')  # all solutions from current user
    num_tasks = solutions.count()  # how tasks did this user try
    correct_solutions = Solution.objects.filter(user=request.user, solved=True).count()  # how many of them were correct?
    if num_tasks > 0:  # calculate percentage of correct tasks (or 0 if no tasks)
        tasks_correctness = round(correct_solutions / num_tasks * 100.0,2)
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
