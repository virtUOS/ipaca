from django import forms

from learning_environment.models import *


class SingleChoiceForm(forms.ModelForm):
    choices = forms.MultipleChoiceField(widget=forms.RadioSelect(),
                                               label=SingleChoice.objects.question, required=True)