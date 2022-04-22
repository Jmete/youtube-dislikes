from django.urls import path
from main_app import views

urlpatterns = [
    path('', views.index, name='main_app_homepage'),
    path('process_url', views.process_url, name='process_url'),
    path('standups', views.standups, name='standups'),
    path('user_select_positive', views.user_select_positive, name='user_select_positive'),
    path('user_select_negative', views.user_select_negative, name='user_select_negative'),
]