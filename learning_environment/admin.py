from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from learning_environment.models import *

admin.site.register(User, UserAdmin)

admin.site.register(Lesson)
admin.site.register(Learner_Lesson)
admin.site.register(Learner)
admin.site.register(Task)
admin.site.register(Learner_Task)
admin.site.register(Module)
admin.site.register(SingleChoice)
admin.site.register(TaskOrder)

# Register your models here.
