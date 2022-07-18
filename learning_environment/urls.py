from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('lesson/',views.lesson, name='lesson'),
    path('singlechoice/', views.singlechoice),
]