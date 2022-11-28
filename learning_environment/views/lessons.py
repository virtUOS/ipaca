"""
View elements to manage lessons and tasks.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView, DetailView, FormView

from learning_environment.forms import LessonCreationForm
from learning_environment.models import Task, Lesson


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
