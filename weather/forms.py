from django import forms
from .weather_services import Weather
import asyncio
from django.core.exceptions import ValidationError


def city_not_found(city):
    weather = asyncio.run(Weather(city).return_weather())
    if weather['cod'] != 200:
        raise ValidationError(f"{weather['message']}")


class CityInputForm(forms.Form):
    city_input_field = forms.CharField(label='',
                                       widget=forms.TextInput(
                                           attrs={'type': "text",
                                                  'class': 'form-control',
                                                  'placeholder': 'London',
                                                  'aria-label': 'City',
                                                  'aria-describedby': 'addon-wrapping',
                                                  'id': 'city_input_field',
                                                  'name': 'city_input_field'}),
                                       max_length=30,
                                       validators=[city_not_found]
                                       )
