from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index_page'),
    path('user/signup', views.add_user, name='insert_new_user'),
    path('user/login', views.user_login, name='login_user'),
    path('user/home', views.render_homepage, name='render_homepage'),
    path('user/logout', views.user_logout, name='render_homepage'),
]
