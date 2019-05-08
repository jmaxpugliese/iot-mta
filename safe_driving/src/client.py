#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2 #pip install opencv-python
import time
import json
import pytz
import boto3
import base64
import _pickle as cPickle
import datetime

capture_rate = 5

class VideoProducer(object):
  '''
  Producer sets up a connection with Amazon Kinesis and sends video frames
  to the server
  '''

  def __init__(self):
    self._stream_name = 'iot-attention-monitor'
    self._kinesis = self.create_aws_client('kinesis')

  def create_aws_client(self, aws_service):
    with open('../aws.json') as aws:  
      config = json.load(aws)

      return boto3.client(
        aws_service,
        aws_access_key_id = config['aws_access_key_id'],
        aws_secret_access_key = config['aws_secret_access_key'],
        region_name = config['aws_region']
      )

  def send_frame(self, frame, frame_count):
    try:
      retval, buff = cv2.imencode(".jpg", frame)
      img_bytes = bytearray(buff)

      utc_dt = pytz.utc.localize(datetime.datetime.now())
      now_ts_utc = (utc_dt - datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()

      frame_package = {
        'ApproximateCaptureTime' : now_ts_utc,
        'FrameCount' : frame_count,
        'ImageBytes' : img_bytes
      }

      resp = self._kinesis.put_record(
                      StreamName=self._stream_name,
                      Data=cPickle.dumps(frame_package),
                      PartitionKey="partitionkey")
      print (resp)
    except Exception as e:
      print(e)

  def run(self):
    try:
      vc = cv2.VideoCapture(0)
      vc.set(3,640)
      vc.set(4,480)
      frame_count = 0
      while True:
        ret, frame = vc.read()

        if ret is False:
          break
        
        if frame_count % capture_rate == 0:
          self.send_frame(frame, frame_count)

        frame_count += 1

        # cv2.imshow('frame', frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    except KeyboardInterrupt:
        self.exit_with_msg('Closing client.', None)
        

if __name__ == '__main__':
    producer = VideoProducer()
    producer.run() 
