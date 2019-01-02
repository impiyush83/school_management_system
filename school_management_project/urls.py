"""school_management_project URL Configuration

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
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('school_management_app.urls')),
    path('/user/signup/', include('school_management_app.urls')),
    path('/user/login/', include('school_management_app.urls')),
    path('/user/home/', include('school_management_app.urls')),
    path('/user/logout/', include('school_management_app.urls')),
    path('/teacher/enroll-student/', include('school_management_app.urls')),
    path('/teacher/student-engagement/', include('school_management_app.urls')),
    path('/teacher/exams/', include('school_management_app.urls')),
    path('/teacher/exams/add', include('school_management_app.urls')),
]

