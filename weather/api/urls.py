from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from . import views

app_name = 'api'

urlpatterns = [
    path('history/', views.search_history_api, name='search_history_api'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='api:schema')),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema')),

]
