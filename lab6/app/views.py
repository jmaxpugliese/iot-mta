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

def source(request, src):
  locations = Location.objects.exclude(name=src)
  context = {
    'source': src,
    'locations': locations
  }
  return render(request, 'app/source.html', context)

def route(request, src, dest):
  src_obj = Location.objects.get(name=src)
  url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=52e9eafa3084f916d19f589607f5aff6'
  src_weather = requests.get(url.format(src)).json()
  src_obj.temperature = src_weather['main']['temp']
  src_obj.save()

  dest_obj = Location.objects.get(name=dest)
  url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=52e9eafa3084f916d19f589607f5aff6'
  dest_weather = requests.get(url.format(dest)).json()
  dest_obj.temperature = dest_weather['main']['temp']
  dest_obj.save()

  context = {
    "src": src,
    "src_temperature": src_weather['main']['temp'],
    "src_icon": src_weather['weather'][0]['icon'],
    "dest": dest,
    "dest_temperature": dest_weather['main']['temp'],
    "dest_icon": dest_weather['weather'][0]['icon']
  }

  return render(request, 'app/route.html', context)


def add_loc(request):
  # If this is a POST request then process the Form data
  if request.method == 'POST':
    Location.objects.create(name=request.POST['loc_name'])
  return HttpResponseRedirect(reverse('app:index'))

    