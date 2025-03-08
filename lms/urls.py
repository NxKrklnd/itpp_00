from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.user_registration, name='user_registration'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('become-trainer/', views.learn_as_trainer, name='learn_as_trainer'),
    path('create-course/', views.create_course, name='create_course'),
]