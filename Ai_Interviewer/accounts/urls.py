from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/hr/', views.register_hr, name='register_hr'),
    path('register/candidate/', views.register_candidate, name='register_candidate'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
