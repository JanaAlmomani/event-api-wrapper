from django.db import models
from django.contrib.auth import get_user_model

class Event(models.Model):
    event_id = models.CharField(max_length=255)
    event_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=100, default='XXX')
    created_at = models.DateTimeField(auto_now_add=True)
    location_x = models.FloatField(max_length=255)
    location_y = models.FloatField(max_length=255)



class Weather(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    temperature = models.FloatField()
    humidity = models.FloatField()


class Flight(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    flight_code = models.CharField(max_length=100)

