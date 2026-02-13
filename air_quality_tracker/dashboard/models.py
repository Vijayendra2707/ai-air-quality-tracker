from django.db import models
from django.contrib.auth.models import User

class AQIHistory(models.Model):
    city = models.CharField(max_length=100)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    aqi = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

class AlertSetting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    threshold = models.IntegerField(default=4)

class RouteHistory(models.Model):
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    fastest_exposure = models.FloatField()
    cleanest_exposure = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

from django.db import models

class AQIRecord(models.Model):
    city = models.CharField(max_length=100)
    aqi = models.FloatField()
    pm25 = models.FloatField(null=True, blank=True)
    pm10 = models.FloatField(null=True, blank=True)
    co = models.FloatField(null=True, blank=True)
    no2 = models.FloatField(null=True, blank=True)
    o3 = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.city} - {self.aqi}"
