#!/usr/bin/python
# -*- coding: utf-8 -*-

import mraa
import math
import json
import time
import boto3

REGION = 'us-east-1'
TOPIC  = 'Temperature in EE Lab'

try:
  with open('config.json') as json_config:  
    config = json.load(json_config)

    client = boto3.client(
      'sns',
      aws_access_key_id = config['aws_access_key_id'],
      aws_secret_access_key = config['aws_secret_access_key'],
      region_name = REGION
    )

    temp_sensor = mraa.Aio(0)
    temp = temp_sensor.read()
    res = float((1023-temp) * 10000/temp)
    temperature = 1 / (math.log(res/10000)/3975 + 1/298.15) - 273.15

    topic = client.create_topic(Name="mtaSub")
    print(topic)
    topic_arn = topic['TopicArn']

    client.subscribe(
        TopicArn=topic_arn,
        Protocol='sms',
        Endpoint='17175722449'  # <-- number who'll receive an SMS message.
    )

    # sent
    print("sent")
    client.publish(Message=temperature, TopicArn=topic_arn)

except KeyboardInterrupt:
  exit
