from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('history/', views.search_history_api, name='search_history_api'),
]
