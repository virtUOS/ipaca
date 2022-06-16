from django.shortcuts import render
from .models import *
from django.views.generic.edit import FormView


#TODO decide which task gets displayed


class Task()
    def __int__(self):
        pass

def task(request):
    context = {
        'title': Task.title,
        'topic': Task.topic,
        'type': Task.type,
        'author': Task.author,
        'source': Task.source,
        'content': Task.content,
        'license': Task.license
    }

    return render(request, 'learning_environment/index.html', context=context)


# Create your views here.
def index(request):
    page = 'index'  # for highlighting current page
    return render(request, 'learning_environment/index.html', locals())
