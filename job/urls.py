"""job URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from system import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('login/',views.AuthLogin.as_view()),
    path('register/',views.RegisterView.as_view()),
    path('logout/',views.LoginOut.as_view()),
    path('index/',views.ProjectListView.as_view()),
    path("pushproject/",views.pushProject.as_view()),
    path("addjob/",views.AddJobView.as_view()),
    path("editjob/",views.EditJobView.as_view()),
    path("adminprojectlist/",views.AdminProjectListView.as_view()),
    path("scorejob/",views.ScoreJobView.as_view())

]
