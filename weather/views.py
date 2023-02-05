from django.shortcuts import render, redirect, reverse
from django.views.generic import View
import asyncio
from .models import CurrentWeatherInDB
from .forms import CityInputForm
from .weather_services import SessionCityList, Weather, convert_to_celsius


def prepare_info_for_render(city, data):
    c_name = data['name']
    country = data['sys']['country']
    temperature, feels_like = convert_to_celsius(data)
    humidity = data['main']['humidity']
    description = data['weather'][0]['description'].capitalize()
    image = data['weather'][0]['icon']
    info_dict = {'city': c_name,
                 'city_del': city,
                 'country': country,
                 'temperature': temperature,
                 'feels_like': feels_like,
                 'humidity': humidity,
                 'description': description,
                 'image': image}  # get only those data what need to show
    return info_dict


def current_weather(request):
    """ Shows weather cards for cities which you are searching for"""
    current_weather_form = CityInputForm()  # create form
    if request.POST.get('delete_city'):
        city_to_delete = request.POST.get('delete_city')
        SessionCityList(request).remove_city_from_session(city_to_delete)
        return redirect('current_weather')
    city_list = SessionCityList(request)  # create empty list with city names
    city = request.POST.get('city_input_field')  # get city from input CityInputForm
    if not city_list.is_city_in_session(city):
        city_list.append_city_in_session(city)
        # add city to session city_list, if city_list is empty -> create and add
    city_list_for_proc = city_list.get_city_list_from_session()
    # return updated city_list for render without duplicates

    try:
        city_list_for_proc.remove(None)
        city_list_for_proc.remove('None')
    except Exception:
        pass

    info = []  # to collect prepared data
    for c in city_list_for_proc:
        weather_in_db = CurrentWeatherInDB(c)
        weather_from_api = Weather(c)
        if weather_in_db.is_city_in_db() and not weather_in_db.is_timestamp_outdated():
            # check if city in DB and weather data is actual
            data = weather_in_db.get_city_data()  # get data from DB
        else:
            data = asyncio.run(weather_from_api.return_weather())  # get through API
            weather_in_db.add_city_data(data)  # save this data in DB and use
        info_for_render = prepare_info_for_render(c, data)  # create info for widget
        info.append(info_for_render)  # populate list that will be rendered
    return render(request, 'current_weather.html', context={'cities': info,
                                                            'city_input_field': current_weather_form
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


def get_city_name_from_input(request):
    """ Process CityInputForm data, store in session and refresh same page"""
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CityInputForm(request.POST)
        if form.is_valid():
            SessionCityList(request).append_city_in_session(form.cleaned_data)
        return redirect(request.path)
