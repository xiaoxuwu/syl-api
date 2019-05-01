from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('login/submit/', views.login_submit_view, name='login_submit'),
    path('logout/', views.logout_view, name='logout'),
]