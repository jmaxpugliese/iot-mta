from django.shortcuts import render

def index(request):
  return render(request, 'temp/index.html', { 'temp': 3 })