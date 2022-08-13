from django import forms
from  crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm


from learning_environment.models import *


class LessonCreationForm(forms.Form):
    pass


class TaskCreationForm(forms.Form):
    pass

class SingleChoiceCreationForm(TaskCreationForm):
    pass

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = Learner
        fields = ('username', 'password1', 'password2')


class SingleChoiceForm(forms.ModelForm):
    '''

    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)


    class Meta:
        model = SingleChoice
        fields = ('answers',)
        widgets = {'answers': forms.RadioSelect}

    #option = forms.MultipleChoiceField(widget=forms.RadioSelect(, required=True,choices = [('1', 'First'), ('2', 'Second')])
  # self.fields['option']. #task.options.split('|')




