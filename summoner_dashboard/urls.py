from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('summoners/<str:region>/<str:summoner_name>', views.summoner_info, name='summoner_info'),
]