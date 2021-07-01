from django.urls import path, re_path

from .views import *


urlpatterns = [
    path('', WomenHome.as_view(), name='home'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
    
    ]
















