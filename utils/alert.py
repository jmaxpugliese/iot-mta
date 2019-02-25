#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Class for alert data
"""


class Alert(object):
    # accepts, optional, alert object
    def __init__(self, a = None):
        self.msg = ''
        self.trip_id = []
        self.route_id = {}
        self.start_date = {}

        if a:
            self.set(a)

    # accepts alert object
    def set(self, a):
        # set message
        for t in a.header_text.translation:
            self.msg = t.text
            break

        # set trip info
        for ie in a.informed_entity:
            self.trip_id.append(ie.trip.trip_id)
            self.route_id = ie.trip.route_id
