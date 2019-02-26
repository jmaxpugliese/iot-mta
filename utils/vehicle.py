#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Class for vehicle data
"""


class Vehicle(object):
    # accepts, optional, vehicle object
    def __init__(self, v=None):
        self.current_stop_number = None
        self.current_stop_id = None
        self.timestamp = None
        self.current_stop_status = None

        if v:
            self.set(v)

    # accepts vehicle object
    def set(self, v):
        self.current_stop_number = v.current_stop_sequence
        self.current_stop_id = v.stop_id
        self.timestamp = v.timestamp
        self.current_stop_status = v.current_status

    def to_string(self):
        return {
            "current_stop_number": self.current_stop_number,
            "current_stop_id": self.current_stop_id,
            "timestamp": self.timestamp,
            "current_stop_status": self.current_stop_status
        }
