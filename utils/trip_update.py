#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict
'''
Collection for trip related data
# Note : some trips wont have vehicle data
'''
class TripUpdate(object):

  # accepts, optional, trip_update object
  def __init__(self, tu=None):
    self.trip_id = None
    self.route_id = None
    self.start_date = None
    self.direction = None
    self.vehicle_data = None

    # Format {stopId : [arrivalTime,departureTime]}
    self.future_stops = OrderedDict()

    if tu:
      self.set(tu)

  # accepts trip_update object
  def set(self, tu):
    self.trip_id = tu.trip.trip_id
    self.route_id = tu.trip.route_id
    self.start_date = tu.trip.start_date

    # if tu.vehicle:
    #   self.set_vehicle(tu)

    for stu in tu.stop_time_update: 
      # set update direction
      self.set_direction(stu.stop_id)

      # insert future stop
      self.add_future_stop(stu)

  def set_direction(self, stop_id):
    self.direction = stop_id[-1]

  def add_future_stop(self, stop):
    self.future_stops[stop.stop_id] = [stop.arrival.time, stop.departure.time]

  # comes from a vehicle entity
  def set_vehicle(self, vehicle):
    self.vehicle_data = vehicle