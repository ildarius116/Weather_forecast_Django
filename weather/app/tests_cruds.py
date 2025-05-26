import requests
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.core.cache import cache

from .models import City, SearchHistory
from .cruds import (
    get_client_ip,
    get_recent_cities_from_db,
    create_city,
    convert_weather_data,
    request_cities,
    get_city_from_web,
    add_search_history_into_db,
    get_search_history_from_db,
)


class CrudsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.city = City.objects.create(
            name='Test City', latitude=51.5074, longitude=-0.1278
        )
        self.weather_data = {
            'current_weather': {
                'temperature': 15.5,
                'windspeed': 10.2,
                'winddirection': 180,
                'weathercode': 3,
                'time': '2023-05-15T12:00'
            },
            'daily': {
                'time': ['2023-05-15', '2023-05-16'],
                'temperature_2m_max': [18.0, 20.0],
                'temperature_2m_min': [12.0, 14.0],
                'weathercode': [3, 1]
            },
            'hourly': {
                'time': ['2023-05-15T00:00', '2023-05-15T01:00'],
                'temperature_2m': [15.0, 14.5],
                'relativehumidity_2m': [80, 75],
                'weathercode': [3, 3]
            }
        }

    def test_get_client_ip_with_x_forwarded_for(self):
        request = self.factory.get('/')
        request.META = {'HTTP_X_FORWARDED_FOR': '192.168.1.1, 10.0.0.1'}
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_with_remote_addr(self):
        request = self.factory.get('/')
        request.META = {'REMOTE_ADDR': '192.168.1.2'}
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.2')

    def test_get_recent_cities_from_db_authenticated(self):
        SearchHistory.objects.create(user=self.user, city=self.city)
        request = self.factory.get('/')
        request.user = self.user
        cities = get_recent_cities_from_db(request)
        self.assertEqual(len(cities), 1)
        self.assertEqual(cities[0].name, 'Test City')

    def test_get_recent_cities_from_db_anonymous(self):
        ip = '192.168.1.1'
        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.META = {'REMOTE_ADDR': ip}

        # Add to cache
        cache_key = f'recent_cities_{ip}'
        cache.set(cache_key, [self.city.id])

        cities = get_recent_cities_from_db(request)
        self.assertEqual(len(cities), 1)
        self.assertEqual(cities[0].name, 'Test City')

    def test_create_city_new(self):
        city = create_city('New City', 40.7128, -74.0060)
        self.assertEqual(city.name, 'New City')
        self.assertEqual(city.latitude, 40.7128)
        self.assertEqual(city.longitude, -74.0060)
        self.assertTrue(City.objects.filter(name='New City').exists())

    def test_create_city_existing(self):
        city = create_city('Test City', 51.5074, -0.1278)
        self.assertEqual(city.id, self.city.id)  # Should return existing city

    def test_convert_weather_data(self):
        current, daily, hourly = convert_weather_data(self.weather_data)

        self.assertEqual(current['temperature'], 15.5)
        self.assertEqual(current['weathercode'], 'Пасмурно')

        self.assertEqual(len(daily), 2)
        self.assertEqual(daily[0]['max_temp'], 18.0)
        self.assertEqual(daily[1]['weather'], 'Преимущественно ясно')

        self.assertEqual(len(hourly), 2)
        self.assertEqual(hourly[0]['humidity'], 80)
        self.assertEqual(hourly[1]['temperature'], 14.5)

    def test_convert_weather_data_empty(self):
        current, daily, hourly = convert_weather_data({})
        expected_current = {
            'temperature': None,
            'windspeed': None,
            'winddirection': None,
            'weathercode': 'Unknown',
            'time': None
        }
        self.assertEqual(current, expected_current)
        self.assertEqual(daily, [])
        self.assertEqual(hourly, [])

    def test_request_cities_local(self):
        for i in range(2, 12):
            City.objects.create(name=f'Test City {i}', latitude=51.5074, longitude=-0.1278)

        cities = request_cities('Test')
        self.assertEqual(len(cities), 10)  # Should return max 10 cities
        self.assertEqual(cities[0]['name'], 'Test City')

    def test_add_search_history_into_db_authenticated(self):
        request = self.factory.get('/')
        request.user = self.user
        request.META = {'REMOTE_ADDR': '192.168.1.1'}
        add_search_history_into_db(request, self.city)
        self.assertTrue(SearchHistory.objects.filter(user=self.user, city=self.city).exists())

    def test_add_search_history_into_db_anonymous(self):
        ip = '192.168.1.1'
        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.META = {'REMOTE_ADDR': ip}

        add_search_history_into_db(request, self.city)

        self.assertTrue(SearchHistory.objects.filter(
            user__isnull=True,
            ip_address=ip,
            city=self.city
        ).exists())

        cache_key = f'recent_cities_{ip}'
        self.assertEqual(cache.get(cache_key), [self.city.id])

    def test_get_search_history_from_db(self):
        SearchHistory.objects.create(user=self.user, city=self.city)
        SearchHistory.objects.create(user=self.user, city=self.city)

        searches, city_stats = get_search_history_from_db(self.user)

        self.assertEqual(len(searches), 2)
        self.assertEqual(len(city_stats), 1)
        self.assertEqual(city_stats[0]['count'], 2)
        self.assertEqual(city_stats[0]['city__name'], 'Test City')


from unittest.mock import patch


class CrudsMockAPITests(TestCase):
    def setUp(self):
        self.city = City.objects.create(
            name='Test City', latitude=51.5074, longitude=-0.1278
        )

    @patch('requests.get')
    def test_request_cities_api(self, mock_get):
        City.objects.create(name='Mock City Local', latitude=51.5074, longitude=-0.1278)

        mock_response = {
            'results': [
                {'name': 'Mock City 1'},
                {'name': 'Mock City 2'}
            ]
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        cities = request_cities('Mock')
        self.assertEqual(len(cities), 3)  # 1 local + 2 from API
        self.assertEqual(cities[0]['name'], 'Mock City Local')
        self.assertEqual(cities[1]['name'], 'Mock City 1')

    @patch('requests.get')
    def test_get_city_from_web_success(self, mock_get):
        mock_response = {
            'results': [
                {
                    'name': 'New City',
                    'latitude': 40.7128,
                    'longitude': -74.0060
                }
            ]
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        city = get_city_from_web('New City')
        self.assertEqual(city.name, 'New City')
        self.assertEqual(city.latitude, 40.7128)
        self.assertTrue(City.objects.filter(name='New City').exists())

    @patch('requests.get')
    def test_get_city_from_web_not_found(self, mock_get):
        mock_response = {'results': []}
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        city = get_city_from_web('Non-existent City')
        self.assertIsNone(city)

    @patch('requests.get')
    def test_get_city_from_web_request_exception(self, mock_get):
        mock_get.side_effect = requests.RequestException('API Error')

        with self.assertRaises(requests.RequestException):
            get_city_from_web('Error City')
