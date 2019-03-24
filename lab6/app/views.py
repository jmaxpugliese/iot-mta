# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import Location

import requests

# Create your views here.
def index(request):
  context = {
    'locations': Location.objects.all()
  }
  return render(request, 'app/index.html', context)

def temp(request, location):
  url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=52e9eafa3084f916d19f589607f5aff6'
  weather = requests.get(url.format(location)).json() #request the API data and convert the JSON to Python data types

  context = {
    "location": location,
    "temperature": weather['main']['temp'],
    "icon": weather['weather'][0]['icon']
  }

  # update db
  location = Location.objects.get(name=location)
  location.temperature = weather['main']['temp']
  location.save()

  return render(request, 'app/temp.html', context)

def add_loc(request):
  # If this is a POST request then process the Form data
  if request.method == 'POST':
    Location.objects.create(name=request.POST['loc_name'])
  return HttpResponseRedirect(reverse('app:index'))

    