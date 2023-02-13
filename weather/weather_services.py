import asyncio
from aiohttp import ClientSession
from django.shortcuts import redirect
from easy_weather.settings import OPEN_WEATHER_API_KEY
from .models import CurrentWeatherInDB


class Weather:
    def __init__(self, city):
        self.city = city
        self.weather_data = {}

    async def get_weather(self):
        """ This function gets weather through API"""
        async with ClientSession() as session:
            url = f'https://api.openweathermap.org/data/2.5/weather'
            params = {'q': self.city, 'APPID': OPEN_WEATHER_API_KEY, 'units': 'metric'}
            async with session.get(url=url, params=params) as response:
                weather_json = await response.json()
                return weather_json

    async def return_weather(self):
        self.weather_data = await self.get_weather()
        return self.weather_data


class SessionCityList:
    def __init__(self, request):
        # self.city_list = []
        self.request = request

        if "city_list" in self.request.session:
            self.city_list = self.request.session["city_list"]
        else:
            self.city_list = self.request.session["city_list"] = []

    def remove_city_from_session(self, city_name):
        """ for the X button """
        if "city_list" in self.request.session:
            self.request.session["city_list"].remove(city_name)
        else:
            raise KeyError('city_list not found in session')
        self.request.session.modified = True

    def is_city_in_session(self, city_name):
        try:
            self.request.session["city_list"].index(city_name)
            return True
        except KeyError:
            return False
        except ValueError:
            return False

    def append_city_in_session(self, city_name):
        """ Check if the key "city_list" exists in the session.
        If it does, we append the new value "city" to the existing list.
        If it doesn't, we create the key "city_list" with the value
        """
        if "city_list" in self.request.session:
            self.request.session["city_list"].append(city_name)
        else:
            self.request.session["city_list"] = [city_name]
        self.request.session.modified = True


def delete_city_if_requested(request):
    city_to_delete = request.POST.get('delete_city')
    SessionCityList(request).remove_city_from_session(city_to_delete)
    return redirect('current_weather')


def add_city_if_requested(city_name, city_list):
    if city_name.is_valid():  # to handle ony input form
        city = city_name.cleaned_data['city_input_field'].capitalize()  # get city from input CityInputForm
        # add city to session city_list, if city_list is empty -> create and add
        if not city_list.is_city_in_session(city) and city is not (None, ''):
            city_list.append_city_in_session(city)


def collect_data_for_city_list(city_list):
    info = []
    for city in city_list.city_list:
        weather_in_db = CurrentWeatherInDB(city)

        if weather_in_db.is_city_in_db() and not weather_in_db.is_timestamp_outdated():
            # check if city in DB and weather data is actual
            data = CurrentWeatherInDB.objects.get(city__exact=city)  # get data from DB
        else:
            weather_from_api = Weather(city)
            api_data = asyncio.run(weather_from_api.return_weather())  # get through API
            weather_in_db.add_city_data(api_data, city)  # save this data in DB and use
            data = CurrentWeatherInDB.objects.get(city__exact=city)
        info.append((city, data))  # populate list with tuples
    return info
