from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from learning_environment.forms import CustomUserCreationForm
from learning_environment.models import ProfileSeriesLevel


class SignUpView(SuccessMessageMixin, generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
    success_message = "User was created successfully. You may now log in."


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
