import sys
import time
import datetime
import json

sys.path.append('./utils')
from mta_updates import MTAUpdates

startoftheday = 1553659200

def getLocalAfter(trips_data, routeId, sourceStopId, time=None):
    result = []
    for trip in trips_data:
        #print type(trip)
        if trip.route_id == "1":
            future_stops = trip.future_stops
            if sourceStopId in future_stops and (time is None or future_stops[sourceStopId][1] >= time):
                print "{}".format(trip.trip_id)
                result.append(trip)
    return result

def getExpressAfter(trips_data, routeId, switchstop, time):
    result = []
    for trip in trips_data:
        if trip.route_id in routeId:
            future_stops = trip.future_stops
            # return the train only if it will leave the "switchstop" after the "time"
            if switchstop in future_stops and future_stops[switchstop][1] >= time:
                print "{}".format(trip.trip_id)
                result.append(trip)
    return result

def getEarliestTrain(trips, destination):
    earliest_time = None
    train_info = None
    for trip in trips:
        future_stops = trip.future_stops
        if destination in future_stops:
            if earliest_time is None or earliest_time > future_stops[destination][0]:
                earliest_time = future_stops[destination][0]
                train_info = trip
    return train_info

def tripPlan(trips_data, src, dst):
    local_trains = getLocalAfter(trips_data, "1", src)
    earliest_local = getEarliestTrain(local_trains, src)
    time_to_96 = earliest_local.future_stops["120S"][0]
    print ("Local train Line({0}{1}) will arrive at {2} station at {3}".format(
            earliest_local.route_id, earliest_local.direction, "96th", time_to_96))

    express_trains = getExpressAfter(trips_data, ["2", "3"], "120S", time_to_96)
    earliest_express = getEarliestTrain(express_trains, "120S")
    print ("Express train Line({0}{1}) will arrive at {2} station at {3}".format(
            earliest_express.route_id, earliest_express.direction, "96th",
            earliest_express.future_stops["120S"][0]))

    noSwitch = earliest_local.future_stops[dst][0]
    start_local = earliest_local.trip_id.split("_")[0]
    doSwitch = earliest_express.future_stops[dst][0]
    start_express = earliest_express.trip_id.split("_")[0]

    print ("Time when arrive at 42nd w/o switch at 96th: w({0}), o({1})".format(doSwitch, noSwitch))

    return ["NOSwitch", start_local, noSwitch] if noSwitch <= doSwitch else ["Switch", start_express, doSwitch]

def mta_get_data(file):
    mta_updater = MTAUpdates()
    mta_updater.update()
    dayofWeek = "Weekday"
    earliest_time = None
    current_ts = None
    start_time = None
    elapsed_time = None
    trips_data = []
    if mta_updater.trip_updates:
        for key in mta_updater.trip_updates:
            route_id = mta_updater.trip_updates[key].route_id
            direction = mta_updater.trip_updates[key].direction
            future_stops = mta_updater.trip_updates[key].future_stops
            current_ts = mta_updater.trip_updates[key].timestamp
            if (route_id == "1" or route_id == "2" or route_id == "3") and direction == "S" and ("120S" in future_stops):
                trips_data.append(mta_updater.trip_updates[key])
        print trips_data
        result = tripPlan(trips_data, "117S", "127S")
        elapsed_time = int(result[2]) - int(current_ts)
        '''
        for key in mta_updater.trip_updates:
            route_id = mta_updater.trip_updates[key].route_id
            direction = mta_updater.trip_updates[key].direction
            future_stops = mta_updater.trip_updates[key].future_stops
            current_ts = mta_updater.trip_updates[key].timestamp
            if (route_id == "1" or route_id == "2" or route_id == "3") and direction == "S" and ("120S" in future_stops):
                if future_stops["120S"][0] > current_ts:
                    vtime = mta_updater.trip_updates[key].vehicle_data.timestamp if mta_updater.trip_updates[key].vehicle_data else None
                    print "viechel time {0}, {1} will arrive at 96th Street at {2}".format(vtime - current_ts if vtime else None, key, int(future_stops["120S"][0]) - int(current_ts))
                    if earliest_time is None or earliest_time > future_stops["120S"][0]:
                        start_time = key.split("_")[0]
                        earliest_time = future_stops["120S"][0]
                        elapsed_time = int(earliest_time) - int(current_ts)
        '''
        res = "{0},{1},{2},{3},{4}\n".format(result[0], current_ts-startoftheday, int(result[1])*60/100, dayofWeek, elapsed_time)
        file.writelines(res)
        print('write!')
    
    time.sleep(20)

def main():
    filepath = './mataData-{}.csv'.format(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
    file = open(filepath, 'w')
    file.write('[\n')
    try:
        while True:
            mta_get_data(file)
    except KeyboardInterrupt:
        file.write(']\n')
        file.close

if __name__ == '__main__':
    main()
