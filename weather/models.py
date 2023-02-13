from django.db import models
from datetime import datetime, timedelta, timezone
from django.shortcuts import reverse


# Create your models here.


class CurrentWeatherInDB(models.Model):
    city = models.CharField(primary_key=True, max_length=85)
    data = models.JSONField(blank=False)
    check_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.city

    def get_absolute_url(self):
        return reverse('detailed_weather', kwargs={'city': self.city})

    def convert_sunrise(self):
        sunrise = self.data['sys']['sunrise']
        dt_object = datetime.fromtimestamp(sunrise, timezone.utc)
        formatted_sunrise = dt_object.strftime('%H:%M %Z')
        return formatted_sunrise

    def convert_sunset(self):
        sunset = self.data['sys']['sunset']
        dt_object = datetime.fromtimestamp(sunset, timezone.utc)
        formatted_sunset = dt_object.strftime('%H:%M %Z')
        return formatted_sunset

    def is_city_in_db(self):
        """ Check if city already in DB"""
        try:
            CurrentWeatherInDB.objects.get(city=self.city)
            return True
        except CurrentWeatherInDB.DoesNotExist:
            return False

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

    def add_city_data(self, city_data, city_name):
        """ Create new entity in DB for the following city and place data gathered from API"""
        city, new = CurrentWeatherInDB.objects.update_or_create(city=city_name, defaults={'data': city_data})
        if not new:
            city.data = city_data
            city.save()
        return city_data

# class ForecastWeather(CurrentWeatherInDB):
#     def certain_day_weather(self):
#         pass
