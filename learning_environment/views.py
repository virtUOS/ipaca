from django.shortcuts import render, redirect

from learning_environment.models import *
from django.views.generic.edit import FormView

# TODO decide which task gets displayed

GLOBAL_CONTEXT = {}


def lesson(request):
    page = 'lesson'
    protagnonist = request.user
    current_lesson = Learner.objects.filter(user = protagnonist , learner_lesson__open= True).learner_lesson__order__max
    current_task = Task.objects.filter(lesson__name=current_lesson.name ).taskorder__order__max


    context = {
        'title': lesson.name,
        'paragraph': lesson.paragraph


    }

    Task.objects.filter(Learner_Task.request.user)

    context.update(GLOBAL_CONTEXT)

    return render(request, 'learning_environment/lesson.html', context=context)


def nexttask(request):

    Task.objects.order_by(lesson_task__order)

        #.filter(learner_task__open= True)



def singlechoice(request):
    SC = Task.objects.get()

    context = {
        'description': SC.description,
        'text': SC.text_element,
        'options': SC.options,

    }

    redirect('learning_environment/lesson.html', context=context)


# Create your views here.
def home(request):
    page = 'home'  # for highlighting current page
    return render(request, 'learning_environment/home.html', locals())
