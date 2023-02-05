from . import views
from django.urls import path

urlpatterns = [
    path('', views.main_weather, name='main_weather'),
    path('current_weather', views.current_weather, name='current_weather'),
    path('forecast', views.forecast, name='forecast'),
]
