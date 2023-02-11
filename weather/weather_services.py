from aiohttp import ClientSession
from easy_weather.settings import OPEN_WEATHER_API_KEY


class Weather:
    def __init__(self, city):
        self.city = city
        self.weather_data = {}

    async def get_weather(self):
        """ This function gets weather through API"""
        async with ClientSession() as session:
            url = f'https://api.openweathermap.org/data/2.5/weather'
            params = {'q': self.city, 'APPID': OPEN_WEATHER_API_KEY}
            async with session.get(url=url, params=params) as response:
                weather_json = await response.json()
                return weather_json

    async def return_weather(self):
        self.weather_data = await self.get_weather()
        return self.weather_data


def convert_to_celsius(data):
    return int(data['main']['temp'] - 273.15), int(data['main']['feels_like'] - 273.15)


class SessionCityList:
    def __init__(self, request):
        self.city_list = []
        self.request = request
        # self.city_name = None  # city name coming from CityInputForm

    def get_city_list_from_session(self):
        if "city_list" in self.request.session:
            self.city_list = self.request.session["city_list"]
        else:
            self.request.session["city_list"] = []
        return self.city_list

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
        # self.city_name = city_name
        if "city_list" in self.request.session:
            self.request.session["city_list"].append(city_name)
        else:
            self.request.session["city_list"] = [city_name]
        self.request.session.modified = True
