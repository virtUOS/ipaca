from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from learning_environment.views.dashboards import global_dashboard, learner_dashboard
from learning_environment.views.lessons import TaskListView, LessonDetailView, LessonCreateView, LessonDeleteView
from learning_environment.views import practice, home, myhome
from learning_environment.views.users import SignUpView, learner_reset

urlpatterns = [
    # Build in
    path('accounts/', include('django.contrib.auth.urls')),

    # Self made
    path('', home, name='home'),
    path('myhome/', myhome, name='myhome'),
    path('practice/', practice, name='practice'),
    path('practice/<int:redo>', practice, name='practice'),
    path('signup/', SignUpView.as_view(), name='signup'),

    # Backstage
    path('backstage/tasklist', TaskListView.as_view(), name='tasklist'),
    path('backstage/lesson/<int:pk>', LessonDetailView.as_view(), name='lessondetail'),
    path('backstage/lesson/create', LessonCreateView.as_view(), name='lessoncreate'),
    path('backstage/lesson/delete/<int:pk>', LessonDeleteView.as_view(), name='lessondelete'),
    path('backstage/dashboard/learner', learner_dashboard, name='learner_dashboard'),
    path('backstage/dashboard/global', global_dashboard, name='global_dashboard'),
    path('backstage/reset', learner_reset, name='learner_reset'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

