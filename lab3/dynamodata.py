# *********************************************************************************************
# Program to update dynamodb with latest data from mta feed. It also cleans up stale entried from db
# Usage python dynamodata.py
# *********************************************************************************************
import json, time, sys
from collections import OrderedDict
from threading import Thread

import boto3
from boto3.dynamodb.conditions import Key,Attr
from utils.mta_updates import MTAUpdates
import utils.aws as aws

### YOUR CODE HERE ####
DYNAMO_TABLE_NAME = 'mtaData'

dynamodb = boto3.resource('dynamodb')
#dynamodb = aws.getResource('dynamodb','us-east-1')
try:
    table = dynamodb.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'tripid',
                'AttributeType': 'S'
            }
        ],
        TableName=DYNAMO_TABLE_NAME,
        KeySchema=[
            {
                'AttributeName': 'tripid',
                'KeyType': 'HASH'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table.meta.client.get_waiter('table_exists').wait(TableName='users')
    print "New Table Created.\n"
except Exception as e:
    table = dynamodb.Table('mtaData')
    print "Table Already Exists.\n"


def data_purge(table):
    while True:
        time.sleep(120)
        expiretime = str(time.time() - 120)
        response = table.scan(
            ScanFilter={"timeStamp": {
                "AttributeValueList": [expiretime],
                "ComparisonOperator": "LE"}}
        )
        for item in response['Items']:
            table.delete_item(
                Key={'tripid': item['tripid']}
            )


def data_update(table):
    mta_updater = MTAUpdates()
    mta_updater.update()



    """
    tripUpdates():
        self.trip_id = None
        self.route_id = None
        self.start_date = None
        self.direction = None
        self.vehicle_data = None
    """


    for key, item in mta_updater.trip_updates:
        table.put_item(Item=item)
    time.sleep(60)


t2 = Thread(name='datapurge', target=data_purge, args=(table,))
t2.setDaemon(True)
t2.start()

try:
    while(True):
        data_update(table)
except KeyboardInterrupt:
    exit