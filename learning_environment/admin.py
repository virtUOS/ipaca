from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile
from learning_environment.models import *

admin.site.register(User, UserAdmin)
admin.site.register(Lesson)
admin.site.register(Task)
admin.site.register(Profile)

# Register your models here.
