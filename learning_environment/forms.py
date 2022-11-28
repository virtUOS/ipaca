from django import forms
from  crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm
from learning_environment.models import User, Lesson
from learning_environment.its.base import Json5ParseException
import json5


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class LessonCreationForm(forms.Form):
    json5 = forms.CharField(widget=forms.Textarea(attrs={'rows': 25}), label="JSON5 code")
    overwrite = forms.BooleanField(label='Overwrite existing Lesson if ID is already in use?', required=False)

    def clean(self):
        """Check if json5 is valid and lesson can be overwritten if exists"""
        cd = self.cleaned_data
        lesson_json5 = cd.get('json5')

        try:
            Lesson.check_json5(lesson_json5)  # parse json and check all fields
        except Json5ParseException as e:
            raise forms.ValidationError("Lesson invalid. Error message: \n"+str(e))

        overwrite = cd.get('overwrite', False)
        if not overwrite:  # if we are allowed to overwrite, then no check is necessary
            l = json5.loads(lesson_json5)  # load json5 structure to get hold of id
            l_id = l['id']
            try:  # looks strange: if we get not DoesNotExist exceptiom, then it exists and we must raise an error
                Lesson.objects.get(lesson_id=l_id)
                raise forms.ValidationError("Lesson with id "+l_id+" already exists and 'overwrite' was not checked.")
            except Lesson.DoesNotExist:
                pass  # it does not exist: test passed

        return cd


class AutomaticLessonCreationForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    name = forms.CharField()
    text_source = forms.CharField()
    text_licence = forms.CharField()
    text_url = forms.URLField()


class EvalLessonForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    name = forms.CharField(widget=forms.HiddenInput())
    text_source = forms.CharField(widget=forms.HiddenInput())
    text_licence = forms.CharField(widget=forms.HiddenInput())
    text_url = forms.URLField(widget=forms.HiddenInput())

    def __init__(self, q_and_a=[], *args, **kwargs):
        super(EvalLessonForm, self).__init__(*args, **kwargs)

        self.num_questions = forms.IntegerField(initial=len(q_and_a), widget=forms.HiddenInput())

        for i, q_a in enumerate(q_and_a):
            q = q_a[0]
            a = q_a[1]
            self.fields[f'Question {i+1}'] = forms.CharField(initial=q, max_length=100)
            self.fields[f'Answer {i+1}'] = forms.CharField(initial=a, max_length=100)

