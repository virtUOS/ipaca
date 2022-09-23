from django import forms
from  crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm
from learning_environment.models import User, Lesson
from .its.tasks import Json5ParseException
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




