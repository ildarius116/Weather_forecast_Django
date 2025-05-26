from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path

from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('get-weather/', views.get_weather, name='get_weather'),
    path('city-autocomplete/', views.city_autocomplete, name='city_autocomplete'),
    path('history/', views.search_history, name='search_history'),
    path('login/', LoginView.as_view(template_name='app/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
