from django.shortcuts import render

# Create your views here.
def index(request):
    page='index' # for highlighting current page
    return render(request, 'learning_environment/index.html', locals())
