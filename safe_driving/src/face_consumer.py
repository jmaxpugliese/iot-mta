#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import time
import boto3

class Consumer(object):

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

      while True:
        kinesis = self.create_aws_client('kinesis')


        response = kinesis.describe_stream(StreamName=self._stream_name)
        my_shard_id = response['StreamDescription']['Shards'][0]['ShardId']
        shard_iterator = kinesis.get_shard_iterator(StreamName=self._stream_name,
                                                      ShardId=my_shard_id,
                                                      ShardIteratorType='LATEST')
                                                      
        my_shard_iterator = shard_iterator['ShardIterator']
        record_response = kinesis.get_records(ShardIterator=my_shard_iterator,
                                            Limit=2)
        while 'NextShardIterator' in record_response:
          record_response = kinesis.get_records(ShardIterator=record_response['NextShardIterator'],
                                                        Limit=2)

          if record_response['Records']:
            print record_response['Records'][0]['Data']

          # wait for 5 seconds
          time.sleep(2)

    except KeyboardInterrupt:
      self.exit_with_msg('Closing client.', None)

if __name__ == '__main__':
    c = Consumer()
    c.run() 