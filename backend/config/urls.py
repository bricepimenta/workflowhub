from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from tasks.views import TaskViewSet,RegisterView,LoginView,LogoutView
router=DefaultRouter(); router.register('tasks',TaskViewSet,basename='task')
urlpatterns=[path('admin/',admin.site.urls),path('api/register/',RegisterView.as_view()),path('api/login/',LoginView.as_view()),path('api/logout/',LogoutView.as_view()),path('api/',include(router.urls))]
