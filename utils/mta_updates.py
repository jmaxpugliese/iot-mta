import pytz
import urllib2
import datetime
import contextlib
import google.protobuf
import gtfs_realtime_pb2

# gtfs objects
from alert import Alert
from vehicle import Vehicle
from trip_update import TripUpdate

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
        self.trip_updates = {}
        # MTA update feed url
        self.feed_url = MTA_URL + MTA_API_KEY

    def update(self):
        """
        :param self: Get trip updates from mta real time feed
        :return:
        """

        # fetch feed from GTFS
        feed = gtfs_realtime_pb2.FeedMessage()

        # check for valid response
        try:
            with contextlib.closing(urllib2.urlopen(self.feed_url)) as response:
                d = feed.ParseFromString(response.read())
        except (urllib2.URLError, google.protobuf.message.DecodeError) as e:
            print "Error while connecting to mta server: " +str(e)

        # parse for timestamp
        timestamp = feed.header.timestamp
        nytime = datetime.datetime.fromtimestamp(timestamp, TIMEZONE)

        # parse feed
        for entity in feed.entity:
            # trip update represents a change in timetable
            if entity.trip_update and entity.trip_update.trip.trip_id:
                # create new trip update
                tu = TripUpdate(entity.trip_update)
                tu.set_timestamp(timestamp)

                # add update to the trip dictionary
                self.trip_updates[tu.trip_id] = tu

            # vehicle update gets added to pre-existing trip update
            if entity.vehicle and entity.vehicle.trip.trip_id:

                # create vehicle
                v = Vehicle(entity.vehicle)

                # add vehicle to trip_update
                tid = entity.vehicle.trip.trip_id
                if self.trip_updates[tid]:
                    self.trip_updates[tid].set_vehicle(v)

            # push new alert
            if entity.alert and entity.alert.informed_entity:
                a = Alert(entity.alert)
                self.alerts.append(a)
                