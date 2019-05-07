#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import json
import time
import boto3
import numpy
import base64
import cPickle
import datetime

class Consumer(object):

  def __init__(self):
    self._stream_name = 'iot-attention-monitor'
    self._shard_id = 'shardId-000000000006'
    self._iterator_type = 'LATEST'

  def create_aws_client(self, aws_service):
    with open('../aws.json') as aws:  
      config = json.load(aws)

      return boto3.client(
        aws_service,
        aws_access_key_id = config['aws_access_key_id'],
        aws_secret_access_key = config['aws_secret_access_key'],
        region_name = config['aws_region']
      )

  @staticmethod
  def iter_records(records):
      for record in records:
          part_key = record['PartitionKey']
          data = record['Data']
          yield part_key, data
  
  def process_records(self, records):
    for part_key, data in self.iter_records(records):

      frame_package_b64 = data
      frame_package = cPickle.loads(frame_package_b64)

      img_bytes = frame_package["ImageBytes"]
      frame_count = frame_package["FrameCount"]

      # print("Writing file img_{}.jpg".format(frame_count))
      # target = open("img_{}.jpg".format(frame_count), 'w')
      # target.write(img_bytes)
      # target.close()

      nparr = numpy.array(img_bytes, dtype=numpy.uint8)
      img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
      gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

      cv2.imshow('frame', gray)
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break
      # time.sleep(2)

  def run(self):
    try:
      kinesis = self.create_aws_client('kinesis')
      response = kinesis.get_shard_iterator(StreamName=self._stream_name, ShardId=self._shard_id,  ShardIteratorType=self._iterator_type)
      
      next_iterator = response['ShardIterator']

      start = datetime.datetime.now()
      finish = start + datetime.timedelta(seconds=30)

      while finish > datetime.datetime.now():
          try:
              response = kinesis.get_records(ShardIterator=next_iterator, Limit=25)

              records = response['Records']

              if records:
                  self.process_records(records)

              next_iterator = response['NextShardIterator']
              time.sleep(0.5)
          except Exception as e:
            print(e)
              # time.sleep(1)

    except KeyboardInterrupt:
      self.exit_with_msg('Closing client.', None)

if __name__ == '__main__':
    c = Consumer()
    c.run() 