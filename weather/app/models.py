from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    search_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Search Histories"
        ordering = ['-search_date']

    def __str__(self):
        return f"{self.user or 'Anonymous'} searched {self.city} at {self.search_date}"
