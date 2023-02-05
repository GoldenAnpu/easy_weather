from django.db import models
from datetime import datetime, timedelta


# Create your models here.


class CurrentWeatherInDB(models.Model):
    city = models.CharField(primary_key=True, max_length=85)
    data = models.JSONField(blank=False)
    check_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.city

    def is_city_in_db(self):
        """ Check if city already in DB"""
        try:
            CurrentWeatherInDB.objects.get(city=self.city)
            return True
        except CurrentWeatherInDB.DoesNotExist:
            return False

    def get_city_data(self):
        """ Get data with weather from DB for current city """
        self.city_data = CurrentWeatherInDB.objects.get(city=self.city)
        return self.city_data.data

    def is_timestamp_outdated(self):
        """ Checks update time in column check_datetime of data in database and compare with current time.
        Data shouldn't be updated more than once an hour.
        """
        self.city_data = CurrentWeatherInDB.objects.get(city=self.city)
        self.check_datetime = self.city_data.check_datetime.replace(tzinfo=None)
        if datetime.utcnow() - self.check_datetime > timedelta(hours=1):
            return True
        else:
            return False

    def add_city_data(self, city_data):
        """ Create new entity in DB for the following city and place data gathered from API"""
        city, new = CurrentWeatherInDB.objects.update_or_create(city=self.city, defaults={'data': city_data})
        if not new:
            city.data = city_data
            city.save()
        return city_data




# class ForecastWeather(CurrentWeatherInDB):
#     def certain_day_weather(self):
#         pass
