from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from learning_environment.models import *

admin.site.register(User, UserAdmin)
admin.site.register(Lesson)
admin.site.register(Task)

# Register your models here.
