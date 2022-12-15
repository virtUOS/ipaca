from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .views import SignUpView
urlpatterns = [
    # Buildin
    path("accounts/", include("django.contrib.auth.urls")),

    # Selfmade
    path('', views.home, name='home'),
    path('myhome/', views.myhome, name='myhome'),
    path('practice/', views.practice, name='practice'),
    path("signup/", SignUpView.as_view(), name="signup"),

    # Backstage
    path('backstage/tasklist', views.TaskListView.as_view(), name='tasklist'),
    path('backstage/lesson/<int:pk>', views.LessonDetailView.as_view(), name='lessondetail'),
    path('backstage/lesson/create', views.LessonCreateView.as_view(), name='lessoncreate'),
    path('backstage/dashboard/learner', views.learner_dashboard, name='learner_dashboard'),
    path('backstage/dashboard/global', views.global_dashboard, name='global_dashboard'),
    path('backstage/reset', views.learner_reset, name='learner_reset'),
    path('backstage/dashboard/solutions_chart', views.solutions_chart, name='solutions_chart'),
    path('backstage/dashboard/progress_chart', views.progress_chart, name='progress_chart'),
    path('backstage/dashboard/questions_chart', views.questions_chart, name='questions_chart'),
    path('backstage/dashboard/users_activity', views.users_activity, name='users_activity'),

    #path('backstage/dashboard/progress_chart', views.plotting, name='progress_chart'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

