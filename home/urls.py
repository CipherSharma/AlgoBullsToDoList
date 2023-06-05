from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.signup_api),
    path("login/",views.login_api),
    path("getTags/", views.get_tags),
    path("createTask/", views.create_task),
    path("getTasks/", views.get_tasks),
    path("getTask/", views.get_task),
    path("updateTask/<str:title>/",views.update_task),
    path("deleteTask/<str:title>/",views.delete_task),
   ]