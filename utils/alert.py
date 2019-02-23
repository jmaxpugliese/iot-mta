#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Class for alert data
'''
class Alert(object):
  
  # accepts, optional, alert object
  def __init__(self, a=None):
    self.msg = ''
    self.trip_id = []
    self.route_id = {}
    self.start_date = {}

    if a:
      self.set(a)

  # accepts alert object
  def set(self, a):
    print('')