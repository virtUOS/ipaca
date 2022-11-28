# basic view login NOT required
from django.shortcuts import render, redirect

from learning_environment.models import Lesson, ProfileSeriesLevel, Profile


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
    request.session.pop('current_lesson', None)
    request.session.pop('current_lesson_todo', None)

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
