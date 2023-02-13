from django import forms
from .weather_services import Weather
import asyncio
from django.core.exceptions import ValidationError


def city_not_found(city):
    weather = asyncio.run(Weather(city).return_weather())
    if weather['cod'] != 200 and 'city not found' in weather['message']:
        raise ValidationError(f"City not found. Please enter a valid city name and try again.", code='city_not_found')


class CityInputForm(forms.Form):
    city_input_field = forms.CharField(
                                        required=False,
                                        label='',
                                        widget=forms.TextInput(
                                            attrs={'type': "text",
                                                   'class': 'form-control',
                                                   'placeholder': 'London',
                                                   'aria-label': 'City',
                                                   'aria-describedby': 'addon_city',
                                                   'id': 'city_input_field',
                                                   'name': 'city_input_field'}),
                                        max_length=30,
                                        validators=[city_not_found]
                                        )
