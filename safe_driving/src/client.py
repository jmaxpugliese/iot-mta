#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2 #pip install opencv-python
import json
import time
import boto3

from imutils.video import VideoStream #pip install imutils

class VideoProducer(object):
  '''
  Client class takes as input a server IP address and port number.
  The client will either (a) put: send a file to the server,
  (b) get: request and receive a file from the server, (c) ls: request
  and recieve a list of files on the server, or (d) exit: exit the session.
  The client connects to the server and sends data based on the chosen action.
  '''

  def __init__(self):
    self._stream_name = 'iot_safe_driver'

  def create_aws_client(self, aws_service):
    with open('../aws.json') as aws:  
      config = json.load(aws)

      return boto3.client(
        aws_service,
        aws_access_key_id = config['aws_access_key_id'],
        aws_secret_access_key = config['aws_secret_access_key'],
        region_name = config['aws_region']
      )

  def run(self):
    try:
      kinesis = self.create_aws_client('kinesis')

      count = 0
      while count < 30:
        kinesis.put_record(
                        StreamName=self._stream_name,
                        Data=json.dumps({'count': count}),
                        PartitionKey="partitionkey")

        print(count)
        time.sleep(3)
        count = count +1

      # vs = VideoStream(src=0).start()
      # fileStream = False
      # time.sleep(1.0)

      # # loop over frames from the video stream
      # count=0
      # while True:
      #   # if this is a file video stream, then we need to check if
      #   # there any more frames left in the buffer to process
      #   if fileStream and not vs.more():
      #     break

      #   # grab the frame from the threaded video file stream, resize
      #   # it, and convert it to grayscale
      #   # channels)
      #   frame = vs.read()
        
      #   gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      #   send_to_server(gray)

    except KeyboardInterrupt:
        self.exit_with_msg('Closing client.', None)
        

if __name__ == '__main__':
    producer = VideoProducer()
    producer.run() 
