#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytz
import urllib2
import datetime
import contextlib
import google.protobuf
import gtfs_realtime_pb2

# feed url depends on the routes to which you want updates
# here we are using feed 1 , which has lines 1,2,3,4,5,6,S
MTA_URL = 'http://datamine.mta.info/mta_esi.php?feed_id=1&key='
MTA_API_KEY = 'e31f03e4730a03bac3d112e6ff677b66'

# Do not change Timezone
TIMEZONE = pytz.timezone('America/New_York')

VCS = {
  1: 'INCOMING_AT',
  2: 'STOPPED_AT',
  3: 'IN_TRANSIT_TO'
}    

class MTAUpdates(object):

  def __init__(self):
    self.alerts = []
    self.tripUpdates = []

    # MTA update feed url
    self.feed_url = MTA_URL + MTA_API_KEY

  def getTripUpdates(self):
    '''
    Get trip updates from mta real time feed
    '''

    # fetch feed from GTFS
    feed = gtfs_realtime_pb2.FeedMessage()

    # check for valid response
    try:
      with contextlib.closing(urllib2.urlopen(self.feed_url)) as response:
        d = feed.ParseFromString(response.read())
    except (urllib2.URLError, google.protobuf.message.DecodeError) as e:
      print "Error while connecting to mta server: " +str(e)

    # parse timestamp
    timestamp = feed.header.timestamp
    nytime = datetime.datetime.fromtimestamp(timestamp, TIMEZONE)

