from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from learning_environment.models import *


class LessonCreationForm(forms.Form):
    pass


class TaskCreationForm(forms.Form):
    pass


class SingleChoiceCreationForm(TaskCreationForm):
    pass


class CustomAuthenticationForm(AuthenticationForm):
    pass


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Learner
        fields = ('username', 'password1', 'password2')


class SingleChoiceForm(forms.Form):
    '''
        Generates the form for a Single choice question
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.form_method = 'post'

        self.helper.add_input(Submit('submit', 'Submit'))

    answers = forms.ModelChoiceField(queryset=Answer.objects.all(), widget=forms.RadioSelect())
