from django.contrib import admin
from django.urls import path, include
from summoner_dashboard import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('summoner_dashboard.urls', 'summoner_dashboard'))),
]
