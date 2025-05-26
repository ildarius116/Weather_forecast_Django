from base64 import b64encode
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import City, SearchHistory
import json


class WeatherViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.city = City.objects.create(name='Test City', latitude=51.5074, longitude=-0.1278)

    def test_index_view(self):
        response = self.client.get(reverse('app:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/index.html')

    def test_autocomplete_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('app:city_autocomplete') + '?query=Test')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('cities', data)

    def test_search_history_requires_login(self):
        response = self.client.get(reverse('app:search_history'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_search_history_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        SearchHistory.objects.create(user=self.user, city=self.city)
        response = self.client.get(reverse('app:search_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/history.html')

    def test_history_api(self):
        self.client.login(username='testuser', password='testpass')
        SearchHistory.objects.create(user=self.user, city=self.city)

        credentials = b64encode(b'testuser:testpass').decode('utf-8')
        response = self.client.get(
            reverse('api:search_history_api'),
            HTTP_AUTHORIZATION=f'Basic {credentials}'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('stats', data)
        self.assertEqual(len(data['stats']), 1)

    def test_weather_submission(self):
        response = self.client.post(reverse('app:get_weather'), {'city': 'London'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(City.objects.filter(name__icontains='London').exists())

    def test_recent_cities_display(self):
        self.client.login(username='testuser', password='testpass')
        SearchHistory.objects.create(user=self.user, city=self.city)
        response = self.client.get(reverse('app:index'))
        self.assertContains(response, 'Test City')
