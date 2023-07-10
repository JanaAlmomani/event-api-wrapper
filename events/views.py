from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Event
from datetime import datetime, timedelta
import requests

@api_view(['GET'])
def event_list(request):
    country_code = request.query_params.get('country_code')
    if not country_code:
        return Response({'error': 'Country code is missing.'}, status=400)

    # Check if data exists in the database and is not more than 6 hours old
    six_hours_ago = datetime.now() - timedelta(hours=6)
    events = Event.objects.filter(country_code=country_code, created_at__gte=six_hours_ago)

    if events:
        # Return the existing data if available
        event_data = [{'id': event.event_id, 'name': event.event_name,'location_x':event.location_x,'location_y':event.location_y} for event in events]
        return Response(event_data)

    # Make a request to the PredictHQ API to fetch the top events in the specified country
    url = f"https://api.predicthq.com/v1/events/?country={country_code}&sort=rank"
    headers = {
        'Authorization': 'Bearer _bQ5-kq6BfexNFSempMuQFXvkwTY0ACZLZ-Ynn0r'
    }
    response = requests.get(url, headers=headers)
    print(response)
    # Check if the request was successful
    if response.status_code == 200:
        # Extract the event data from the response
        data = response.json().get('results', [])
        events = []

        # Process each event and extract relevant information
        for event in data:
            event_data = {
                'id': event['id'],
                'name': event['title'],
                'location_x': event['location'][0],
                'location_y': event['location'][1],
                # Add other event details as needed
            }
            events.append(event_data)

        # Save the fetched events in the database for future queries
        for event_data in events:
            Event.objects.create(
                country_code=country_code,
                event_name=event_data['name'],
                event_id=event_data['id'],
                location_x=event_data['location_x'],
                location_y=event_data['location_y']
                # Save other event details as needed
            )

        return Response(events)

    # Return an empty list if there was an error or no events found
    return Response([], status=response.status_code)


@api_view(['GET'])
def weather(request):

    event_id = request.query_params.get('event_id', '')

    event_url = f"https://api.predicthq.com/v1/events/?id={event_id}"
    print(event_url)
    event_response = requests.get(
        event_url,
        headers={
            "Authorization": "Bearer EqpJf87ypBIW6cbbhkXRj_HOyxkNezMRw66NdI86",
            "Accept": "application/json"
        }
    ).json()
    print(event_response)

    event = event_response['results'][0]
    lon = event['location'][0]
    lat = event['location'][1]

    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=f22892654725839a44ff6db985f0b151"
    req = requests.get(weather_url)


    # Check if the request was successful
    if req.status_code == 200:
        # Extract the weather data from the response
        data = req.json()
        temperature = data['main']['temp']
        humidity = data['main']['humidity']

        # Prepare the weather information response
        weather_info = {
            'temperature': temperature,
            'humidity': humidity
        }

        return Response(weather_info)
    
    # Return an error if there was an issue with the API request
    return Response({'error': 'Failed to fetch weather information.'}, status=req.status_code)


@api_view(['GET'])
def flights(request):
    iata_code = request.query_params.get('flight_code')

    event_id = request.query_params.get('event_id', '')

    event_url = f"https://api.predicthq.com/v1/events/?id={event_id}"
    event_response = requests.get(
        event_url,
        headers={
            "Authorization": "Bearer EqpJf87ypBIW6cbbhkXRj_HOyxkNezMRw66NdI86",
            "Accept": "application/json"
        }
    ).json()

    event = event_response['results'][0]
    lon = event['location'][0]
    lat = event['location'][1]

    flight_url = f"https://airlabs.co/api/v9/nearby?lat={lat}&lng={lon}&distance=200&api_key=fda80c93-1fbc-4225-850c-4ca1a40b7de8"
    req = requests.get(flight_url)
    api_data = req.json()
    if api_data.get("response"):
        data=api_data["response"]["airports"][0]['iata_code']

        url_going = f'https://airlabs.co/api/v9/schedules?dep_iata={iata_code}&arr_iata={data}&api_key=7fe8c5aa-d035-4298-9a12-443dbbd3b65c'
        req = requests.get(url_going)
        going_data=req.json()
        print(going_data)
        data_going=going_data["response"]


        url_coming = f'https://airlabs.co/api/v9/schedules?dep_iata={data}&arr_iata={iata_code}&api_key=7fe8c5aa-d035-4298-9a12-443dbbd3b65c'
        req = requests.get(url_coming)
        coming_data=req.json()
        data_coming=coming_data["response"]


        flights_info = {
            'data_going': data_going,
            'data_coming': data_coming
        }

        return Response(flights_info)

    return Response({'error': 'Failed to fetch airports information.'}, status=req.status_code)

