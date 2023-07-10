from django.urls import path
from events.views import event_list, weather,flights
# , weather, flights

urlpatterns = [
    path('list/', event_list, name='event_list'),
    path('weather/', weather, name='weather'),
    path('flights/', flights, name='flights'),
]
