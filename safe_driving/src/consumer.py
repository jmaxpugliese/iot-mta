#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import json, time
import boto3, numpy, base64, datetime, threading, dlib
import _pickle as cPickle

import face_reader

DAT_FILENAME = '../src/shape_predictor_68_face_landmarks.dat'

class Consumer(object):
  def __init__(self):
    self._stream_name = 'iot-attention-monitor'
    self._shard_id = 'shardId-000000000006'
    self._iterator_type = 'LATEST'

    self.eyes_closed_consecutive_frames = 0
    self.looking_away_consecutive_frames = 0
    self.eyeOpen = True
    self.lookAhead = True

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
  
  def get_info(self):
    return {
      'eye': self.eyeOpen,
      'head': self.lookAhead
    }

  def process_records(self, records):
    detector=dlib.get_frontal_face_detector()
    predictor=dlib.shape_predictor(DAT_FILENAME)
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

      if gray is None:
        break

      eyes_open, looking_forward = face_reader.process_frame(detector,predictor,gray)

      if eyes_open is True:
        self.eyes_closed_consecutive_frames = 0
        self.eyeOpen = True
      else:
        self.eyes_closed_consecutive_frames += 1
        if self.eyes_closed_consecutive_frames > 3:
          self.eyeOpen = False
      
      if looking_forward is True:
        self.looking_away_consecutive_frames = 0
        self.lookAhead = True
      else:
        self.looking_away_consecutive_frames += 1
        if self.looking_away_consecutive_frames > 3:
          self.lookAhead = False
      # cv2.imshow('frame', gray)
      

  def run(self):
    try:
      kinesis = self.create_aws_client('kinesis')
      response = kinesis.get_shard_iterator(StreamName=self._stream_name, ShardId=self._shard_id,  ShardIteratorType=self._iterator_type)
      
      next_iterator = response['ShardIterator']

      # start = datetime.datetime.now()
      # finish = start + datetime.timedelta(seconds=30)

      while True:
        try:
          response = kinesis.get_records(ShardIterator=next_iterator, Limit=30)

          records = response['Records']

          if records:
              self.process_records(records)

          next_iterator = response['NextShardIterator']
          time.sleep(0.5)
        except Exception as e:
          print(e)

    except KeyboardInterrupt:
      self.exit_with_msg('Closing client.', None)
