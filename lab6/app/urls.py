from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add_location/', views.add_loc, name='add_loc'),
    # ex: /app/New%20York/
    # url(r'^(.*)/$', views.temp, name='temp'),
    url(r'source/(.*)/$', views.source, name='source'),
    url(r'source/(.*)/destination/(.*)$', views.route, name='route'),
]