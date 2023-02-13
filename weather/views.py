from django.shortcuts import render
from easy_weather.settings import GOOGLE_MAPS_API_KEY
from .models import CurrentWeatherInDB
from .forms import CityInputForm
from .weather_services import SessionCityList, delete_city_if_requested, add_city_if_requested, collect_data_for_city_list


def current_weather(request):
    """ Shows weather cards for cities which you are searching for"""
    session_city_list = SessionCityList(request)
    if request.method == "POST":
        if request.POST.get('delete_city'):
            delete_city_if_requested(request)
            city_name = CityInputForm()
        else:
            city_name = CityInputForm(request.POST)  # create form
            add_city_if_requested(city_name, session_city_list)
    else:
        city_name = CityInputForm()
    # get list with city names from session or create empty if session doesn't have any
    info = collect_data_for_city_list(session_city_list)  # to collect prepared data
    return render(request, 'current_weather.html', context={'cities': info,
                                                            'city_input_field': city_name,
                                                            })


def forecast(request):
    city_list = CurrentWeatherInDB.objects.order_by('city')
    info = []
    for c in city_list:
        info_string = f"{c.city}: {c.data}"
        info.append(info_string)
    return render(request, 'forecast.html', context={'cities': info})


def main_weather(request):
    return render(request, 'main_weather.html')


def detailed_weather(request, city):
    city_data = CurrentWeatherInDB.objects.get(city__exact=city)
    return render(request, 'detailed_weather.html', context={'data': city_data, 'API_KEY': GOOGLE_MAPS_API_KEY})
