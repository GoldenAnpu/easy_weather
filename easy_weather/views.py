from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect

import weather.views


# Create your views here.


def main_page(request):
    return HttpResponseRedirect(reverse(weather.views.main_weather))
