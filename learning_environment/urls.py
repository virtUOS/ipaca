from django.urls import path, include

from . import views
from .views import SignUpView

urlpatterns = [
    # Buildin
    path("accounts/", include("django.contrib.auth.urls")),


    # Selfmade
    path('', views.home, name='home'),
    path('nexttask/',views.nexttask, name='nexttask'),
    path("signup/", SignUpView.as_view(), name="signup"),


]