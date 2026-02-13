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
