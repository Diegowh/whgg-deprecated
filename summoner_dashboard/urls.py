from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('summoners/euw1/<str:summoner_name>', views.summoner_info, name='summoner_info'),
]