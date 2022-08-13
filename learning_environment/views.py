from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages

from learning_environment.models import *
from .forms import *
from django.views.generic.edit import FormView


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"




@login_required
def nexttask(request):






    protagonist = request.user #user=protagonist,
    current_lesson = Learner_Lesson.objects.filter(learner=protagonist, open = True).order_by('order').first().lesson
    current_task = TaskOrder.objects.filter(lesson=current_lesson,task__in=Learner_Task.objects.filter(learner = protagonist, open = True).values_list('task',flat=True)).first().task




    if current_task.interaction == 'SC':
        current_task = SingleChoice.objects.get(title = current_task.title)

        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = SingleChoiceForm(request.POST)

            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                

                return render(request,'learning_environment/home.html')

            # if a GET (or any other method) we'll create a blank form
        else:
            form = SingleChoiceForm()

        context = {
            'lesson': current_lesson,
            'task': current_task,
            'form': form
        }
        return render(request,'learning_environment/singlechoice.html', context=context)

    return render(request,'learning_environment/lesson.html', context=context)



# basic view login NOT required
def home(request):
    page = 'home'  # for highlighting current page
    return render(request, 'learning_environment/home.html', locals())
