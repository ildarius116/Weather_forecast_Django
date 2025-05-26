import requests
from django.core.cache import cache
from django.db import models
from typing import List

from .models import City, SearchHistory


def get_client_ip(request) -> int:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_recent_cities_from_db(request) -> list:
    if request.user.is_authenticated:
        recent_searches = SearchHistory.objects.filter(user=request.user).order_by('-search_date')[:5]
        recent_cities = [search.city for search in recent_searches]
    else:
        ip = get_client_ip(request)
        cache_key = f'recent_cities_{ip}'
        recent_cities_data = cache.get(cache_key, [])
        recent_cities = City.objects.filter(id__in=recent_cities_data)
    return recent_cities


def create_city(name, latitude, longitude) -> City:
    city, created = City.objects.get_or_create(
        name=name,
        defaults={
            'latitude': latitude,
            'longitude': longitude,
        }
    )
    return city


def convert_weather_data(weather_data) -> tuple[dict, List[dict], List[dict]]:
    current = weather_data.get('current_weather', {})
    daily = weather_data.get('daily', {})
    hourly = weather_data.get('hourly', {})

    weather_codes = {
        0: 'Ясно',
        1: 'Преимущественно ясно',
        2: 'Переменная облачность',
        3: 'Пасмурно',
        45: 'Туман',
        48: 'Туман с инеем',
        51: 'Легкая морось',
        53: 'Умеренная морось',
        55: 'Сильная морось',
        56: 'Легкая ледяная морось',
        57: 'Сильная ледяная морось',
        61: 'Небольшой дождь',
        63: 'Умеренный дождь',
        65: 'Сильный дождь',
        66: 'Легкий ледяной дождь',
        67: 'Сильный ледяной дождь',
        71: 'Небольшой снег',
        73: 'Умеренный снег',
        75: 'Сильный снег',
        77: 'Снежные зерна',
        80: 'Небольшие ливни',
        81: 'Умеренные ливни',
        82: 'Сильные ливни',
        85: 'Небольшие снегопады',
        86: 'Сильные снегопады',
        95: 'Гроза',
        96: 'Гроза с небольшим градом',
        99: 'Гроза с сильным градом'
    }

    current_weather = {
        'temperature': current.get('temperature'),
        'windspeed': current.get('windspeed'),
        'winddirection': current.get('winddirection'),
        'weathercode': weather_codes.get(current.get('weathercode'), 'Unknown'),
        'time': current.get('time')
    }

    daily_forecast = []
    if daily and 'time' in daily and 'temperature_2m_max' in daily:
        for i in range(len(daily['time'])):
            daily_forecast.append({
                'date': daily['time'][i],
                'max_temp': daily['temperature_2m_max'][i],
                'min_temp': daily['temperature_2m_min'][i],
                'weather': weather_codes.get(daily['weathercode'][i], 'Unknown')
            })

    hourly_forecast = []
    if hourly and 'time' in hourly and 'temperature_2m' in hourly:
        for i in range(0, min(24, len(hourly['time']))):
            hourly_forecast.append({
                'time': hourly['time'][i],
                'temperature': hourly['temperature_2m'][i],
                'humidity': hourly['relativehumidity_2m'][i],
                'weather': weather_codes.get(hourly['weathercode'][i], 'Unknown')
            })
    return current_weather, daily_forecast, hourly_forecast


def request_cities(city_name) -> List[dict]:
    cities = City.objects.filter(name__istartswith=city_name).values('name')[:10]

    if len(cities) < 10:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            'name': city_name,
            'count': 10 - len(cities),
            'language': 'en',
            'format': 'json'
        }

        try:
            response = requests.get(geo_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get('results'):
                api_cities = [{'name': result['name']} for result in data['results']]
                cities = list(cities) + api_cities
        except requests.RequestException:
            pass
    return cities


def get_city_from_web(city_name) -> City | None:
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        'name': city_name,
        'count': 1,
        'language': 'en',
        'format': 'json'
    }

    try:
        response = requests.get(geo_url, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('results'):
            city = create_city(name=data['results'][0]['name'],
                               latitude=data['results'][0]['latitude'],
                               longitude=data['results'][0]['longitude'],
                               )
            return city
        else:
            return None
    except requests.RequestException:
        raise requests.RequestException


def add_search_history_into_db(request, city) -> None:
    ip = get_client_ip(request)
    if request.user.is_authenticated:
        SearchHistory.objects.create(user=request.user, city=city, ip_address=ip)
    else:
        SearchHistory.objects.create(city=city, ip_address=ip)
        cache_key = f'recent_cities_{ip}'
        recent_cities = cache.get(cache_key, [])
        if city.id not in recent_cities:
            recent_cities.insert(0, city.id)
            recent_cities = recent_cities[:5]
            cache.set(cache_key, recent_cities, 60 * 60 * 24 * 7)


def get_search_history_from_db(user) -> tuple[List[str], List[str]]:
    searches = SearchHistory.objects.filter(user=user).select_related('city').order_by('-search_date')

    city_stats = SearchHistory.objects.filter(user=user) \
        .values('city__name') \
        .annotate(count=models.Count('id')) \
        .order_by('-count')

    return searches, city_stats
