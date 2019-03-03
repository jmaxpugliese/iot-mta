# *********************************************************************************************
# Program to update dynamodb with latest data from mta feed. It also cleans up stale entried from db
# Usage python dynamodata.py
# *********************************************************************************************
from boto3.dynamodb.conditions import Key, Attr
from collections import OrderedDict
from threading import Thread
import time, sys, boto3
# local packages
sys.path.append('./utils')
from mta_updates import MTAUpdates
import aws as aws

### YOUR CODE HERE ####
DYNAMO_TABLE_NAME = 'mtaData'

# dynamodb = boto3.resource('dynamodb')
dynamodb = aws.getResource('dynamodb','us-east-1')

try:
    table = dynamodb.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'trip_id',
                'AttributeType': 'S'
            }
        ],
        TableName=DYNAMO_TABLE_NAME,
        KeySchema=[
            {
                'AttributeName': 'trip_id',
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
        time.sleep(60)
        print("purging...")
        expiretime = str(time.time() - 120)
        response = table.scan(
            ScanFilter={"timestamp": {
                "AttributeValueList": [expiretime],
                "ComparisonOperator": "LE"}
                }
        )
        for item in response['Items']:
            table.delete_item(
                Key={'trip_id': item['trip_id']}
            )


def data_update(table):
    mta_updater = MTAUpdates()
    mta_updater.update()

    for key in mta_updater.trip_updates:
        # print(mta_updater.trip_updates[key])
        table.put_item(Item=mta_updater.trip_updates[key].to_json())
    print('put!')
    time.sleep(30)


t2 = Thread(name='datapurge', target=data_purge, args=(table,))
t2.setDaemon(True)

try:
    t2.start()
    while(True):
        data_update(table)
except KeyboardInterrupt:
    exit
