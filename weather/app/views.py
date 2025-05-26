import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .cruds import (
    add_search_history_into_db,
    convert_weather_data,
    get_city_from_web,
    get_recent_cities_from_db,
    get_search_history_from_db,
    request_cities,
)
from .models import City


def index(request):
    location_city = None
    recent_cities = get_recent_cities_from_db(request)

    return render(request, 'app/index.html', {
        'recent_cities': recent_cities,
        'location_city': location_city,
        'user': request.user,
    })


def get_weather(request):
    if request.method == 'POST':
        city_name = request.POST.get('city')
        city = City.objects.filter(name__iexact=city_name).first()

        if not city:
            try:
                city = get_city_from_web(city_name)

                if not city:
                    return render(request, 'app/index.html', {
                        'error': 'Город не найден. Пожалуйста, попробуйте другое название.'
                    })

            except requests.RequestException:
                return render(request, 'app/index.html', {
                    'error': 'Не удалось подключиться к сервису геокодинга. Пожалуйста, попробуйте позже.'
                })

        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': city.latitude,
            'longitude': city.longitude,
            'current_weather': 'true',
            'hourly': 'temperature_2m,relativehumidity_2m,weathercode',
            'daily': 'weathercode,temperature_2m_max,temperature_2m_min',
            'timezone': 'auto'
        }

        try:
            response = requests.get(weather_url, params=params)
            response.raise_for_status()
            weather_data = response.json()

            add_search_history_into_db(request, city)
            current_weather, daily_forecast, hourly_forecast = convert_weather_data(weather_data=weather_data)

            return render(request, 'app/index.html', {
                'city': city,
                'current': current_weather,
                'daily_forecast': daily_forecast,
                'hourly_forecast': hourly_forecast
            })

        except requests.RequestException:
            return render(request, 'app/index.html', {
                'error': 'Не удалось подключиться к сервису погоды. Пожалуйста, попробуйте позже.'
            })

    return redirect('index')


def city_autocomplete(request):
    query = request.GET.get('query', '')
    if len(query) >= 2:
        cities = request_cities(city_name=query)

        return JsonResponse({'cities': [city['name'] for city in cities]})
    return JsonResponse({'cities': []})


def search_history(request):
    if not request.user.is_authenticated:
        return redirect('app:index')

    searches, city_stats = get_search_history_from_db(user=request.user)

    return render(request, 'app/history.html', {
        'searches': searches,
        'city_stats': city_stats
    })
