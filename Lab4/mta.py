#**********************************************************************************************
# * Copyright (C) 2015-2016 Sareena Abdul Razak sta2378@columbia.edu
# * 
# * This file is part of New-York-MTA-Subway-Trip-Planner.
# * 
# * New-York-MTA-Subway-Trip-Planner can not be copied and/or distributed without the express
# * permission of Sareena Abdul Razak
# * Edited by Peter Wei pw2428@columbia.edu, February 19, 2018
# *********************************************************************************************
# Usage python mta.py

from boto3.dynamodb.conditions import Key, Attr
from threading import Thread
import time, csv, sys, boto3, json
# local package
sys.path.append("./utils")
import aws as aws

# Constants
DYNAMODB_TABLE_NAME = "mtaData"
DEBUG = True
with open('Lab4/config.json') as json_config:  
    config = json.load(json_config)
    client = boto3.client(
        'sns',
        aws_access_key_id = config['aws_access_key_id'],
        aws_secret_access_key = config['aws_secret_access_key'],
        region_name = config['aws_region']
    )
    topic = client.create_topic(Name="mtaSub")
    topic_arn = topic['TopicArn']

dynamodb = aws.getResource("dynamodb","us-east-1")

def Dprint(context):
    if DEBUG:
        print context

# prompt
def prompt():
    print ""
    print "> Available Commands are: "
    print "1. plan trip"
    print "2. subscribe to message feed"
    print "3. exit"  

def buildStationssDB():
    stations = []
    with open("Lab4/stops.csv", "rb") as f:
        reader = csv.reader(f)
        for row in reader:
            stations.append(row[0])
    return stations[1:]


##############################################
# YOU MAY USE THESE METHODS, OR CODE YOUR OWN
##############################################
# Method to get all local going in a given direction on a give routeId and havent passed sourceStopId
def getLocalAfter(table, direction, routeId, sourceStopId, time=None):
    ###############################
    # YOUR CODE HERE #
    ###############################
    result = []
    trips_data = table.scan(
            FilterExpression=Attr("route_id").eq(routeId) &
                             Attr("direction").eq(direction)
        )

    for trip in trips_data["Items"]:
        #print type(trip)
        future_stops = trip["future_stops"]
        if sourceStopId in future_stops and (True if time is None else future_stops[sourceStopId][1] >= time):
            print "{}".format(trip["trip_id"])
            result.append(trip)
    
    return result

# Method to get all express going in a given direction on a give routeId and are at a given stop after some"time"
def getExpressAfter(table, direction, routeId, stop, time=None):
    ###############################
    # YOUR CODE HERE #
    ###############################
    result = []
    trips = table.scan(
        FilterExpression=Attr("route_id").eq(routeId[0]) |
                         Attr("route_id").eq(routeId[1]) &
                         Attr("direction").eq(direction)
    )
    for trip in trips["Items"]:
        future_stops = trip["future_stops"]
        # return the train only if it will leave "stop" after the "time"
        if stop in future_stops and (True if time is None else future_stops[stop][1] >= time):
            print "{}".format(trip["trip_id"])
            result.append(trip)

    return result

# Method to get the earliest train's data
def getEarliestTrain(trips, destination):
    ###############################
    # YOUR CODE HERE #
    ###############################
    earliest_time = None
    train_info = None
    for trip in trips:
        future_stops = trip["future_stops"]
        if destination in future_stops:
            if earliest_time is None or earliest_time > future_stops[destination][0]:
                earliest_time = future_stops[destination][0]
                train_info = trip

    return train_info

def getTimeToReachDestination(trip, destination):
    ###############################
    # YOUR CODE HERE #
    ###############################

    return trip["future_stops"][destination][0]

def tripPlan(table, src, dst, dir):
    Dprint("Current timestamp is {}".format(time.time()))
    if dir == "S":
        local_trains = getLocalAfter(table, dir, "1", src)
        earliest_local = getEarliestTrain(local_trains, src)
        time_to_96 = earliest_local["future_stops"]["120S"][0]
        Dprint("Local train Line({0}{1}) will arrive at {2} station at {3}".format(
                earliest_local["route_id"], earliest_local["direction"], "96th", time_to_96))

        express_trains = getExpressAfter(table, dir, ["2", "3"], "120S", time_to_96)
        earliest_express = getEarliestTrain(express_trains, "120S")
        Dprint("Express train Line({0}{1}) will arrive at {2} station at {3}".format(
                earliest_express["route_id"], earliest_express["direction"], "96th",
                earliest_express["future_stops"]["120S"][0]))

        noSwitch = getTimeToReachDestination(earliest_local, "127S")
        doSwitch = getTimeToReachDestination(earliest_express, "127S")

        Dprint("Time when arrive at 42nd w/o switch at 96th: w({0}), o({1})".format(doSwitch, noSwitch))

        if noSwitch <= doSwitch:
            sendMessage( "Stay on the Local Train!")
        else:
            sendMessage( "Switch to Express Train!")
    else:
        local_trains = getLocalAfter(table, dir, "1", "127N")
        earliest_local = getEarliestTrain(local_trains, "127N")
        Dprint("Local train Line({0}{1}) will arrive at {2} station at {3}".format(
                earliest_local["route_id"], earliest_local["direction"],
                "42nd", earliest_local["future_stops"]["127N"][0]))

        express_trains = getExpressAfter(table, dir, ["2", "3"], "127N")
        earliest_express = getEarliestTrain(express_trains, "127N")
        time_to_96 = earliest_express["future_stops"]["120N"][0]
        Dprint("Express train Line({0}{1}) will arrive at {2} station at {3}".format(
                earliest_express["route_id"], earliest_express["direction"],
                "42nd", earliest_express["future_stops"]["127N"][0]))

        local_trains_after = getLocalAfter(table, dir, "1", "120N", time_to_96)
        earliest_local_after = getEarliestTrain(local_trains_after, "120N")
        
        noSwitch = getTimeToReachDestination(earliest_local, dst)
        doSwitch = getTimeToReachDestination(earliest_local_after, dst)

        Dprint("Time when arrive at 42nd w/o switch at 96th: w({0}), o({1}).".format(doSwitch, noSwitch))

        if noSwitch <= doSwitch:
            sendMessage( "Stay on the Local Train!")
        else:
            sendMessage( "Switch to Express Train!")

    return

def sendMessage(msg):
    resp = client.publish(Message=msg, TopicArn=topic_arn)
    Dprint('sent: ' + msg)
    Dprint(resp)

def addSubcriber(phoneNumber):
    client.subscribe(
        TopicArn=topic_arn,
        Protocol='sms',
        Endpoint=phoneNumber #phoneNumber # <-- number who'll receive an SMS message.
    )
    print "Success! Now {} will receive notifications!".format(phoneNumber)


def main():
    dynamoTable = dynamodb.Table(DYNAMODB_TABLE_NAME)

    # Get list of all stopIds
    stations = buildStationssDB()

    while True:
        prompt()
        sys.stdout.write("> select a command : ")
        userIn = sys.stdin.readline().strip()
        if len(userIn) < 1 :
            print "Command not recognized"
        else:
            if userIn == "1":
                sys.stdout.write("> Enter source : ")
                sourceStop = sys.stdin.readline().strip()
                if sourceStop not in stations:
                    sys.stdout.write("> Invalid stop id. Enter a valid stop id")
                    sys.stdout.flush()
                    continue
                else:
                    if sourceStop[-1] in ["N","S"]:
                        sourceStop = sourceStop[:-1]

                sys.stdout.write("> Enter destination : ")
                destinationStop = sys.stdin.readline().strip()
                if destinationStop not in stations:
                    sys.stdout.write("> Invalid stop id. Enter a valid stop id")
                    sys.stdout.flush()
                    continue
                else:
                    if destinationStop[-1] in ["N","S"]:
                        destinationStop = destinationStop[:-1]

                sys.stdout.write("> Type N for uptown, S for downtown: ")
                direction = sys.stdin.readline().strip()

                # Validate direction
                if direction not in ["N","S"]:
                    sys.stdout.write("> Invalid direction. Enter a valid direction")
                    sys.stdout.flush()
                    continue
                ###############################
                # YOUR CODE HERE #
                ###############################
                if direction == "S":
                    if sourceStop > "120" or destinationStop != "127":
                        print "Unsupported trip!"
                        continue
                else:
                    if destinationStop > "120" or sourceStop != "127":
                        print "Unsupported trip!"
                        continue
                tripPlan(dynamoTable, sourceStop+direction, destinationStop+direction, direction)
            elif userIn == "2":
                sys.stdout.write("> Enter phonenumber: ")
                phoneNumber = sys.stdin.readline().strip()
                ###############################
                # YOUR CODE HERE #
                ###############################
                addSubcriber(phoneNumber)

            else:
                sys.exit()


if __name__ == "__main__":
    main()
    

   

        
