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


class LogInView(generic.CreateView):
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy("update")
    template_name = "registration/login.html"




@login_required
def nexttask(request):
    context = {}
    protagonist = request.user


    current_lesson = LessonOrder.objects.filter(lesson__in= Learner_Lesson.objects.filter(learner=protagonist,open=True).values_list('lesson',flat=True)).order_by('order').first().lesson


    current_task = TaskOrder.objects.filter(lesson=current_lesson,
                                            task__in=Learner_Task.objects.filter(learner=protagonist,
                                                                                 open=True).values_list('task',
                                                                                                        flat=True)).order_by('order').first().task

    if current_task.interaction == 'SC':
        current_task = SingleChoice.objects.get(title=current_task.title)

        if request.method == 'POST':
            form = SingleChoiceForm(request.POST)
            if form.is_valid():
                current_answer = form.cleaned_data['answers']
                Learner_Task.objects.get(learner=protagonist, task=current_task).answer = current_answer
                Learner_Task.objects.get(learner=protagonist, task=current_task).open = False
                Learner_Task.objects.get(learner=protagonist, task=current_task).correct = TaskAnswer.objects.get(
                    task=current_task, answer=current_answer).value == 1


                return redirect('home')




        else:
            form = SingleChoiceForm()

        context = {
            'lesson': current_lesson,
            'task': current_task,
            'form': form
        }
        return render(request, 'learning_environment/singlechoice.html', context=context)

    return render(request, 'learning_environment/lesson.html', context=context)




@login_required
def update_learner_relations(request):
    protagonist = Learner.objects.get(id=request.user.id)
    for t in Task.objects.all():
        if t in [i.task for i in Learner_Task.objects.filter(learner=protagonist).all()]:
            continue
        Learner_Task.objects.create(learner=Learner.objects.get(id=request.user.id), task=t)
    for l in Lesson.objects.all():
        if l in [i.lesson for i in Learner_Lesson.objects.filter(learner=protagonist).all()]:
            continue
        Learner_Lesson.objects.create(learner=Learner.objects.get(id=request.user.id), lesson=l)


    return redirect('home')


# basic view login NOT required
def home(request):
    page = 'home'  # for highlighting current page
    return render(request, 'learning_environment/home.html', locals())
