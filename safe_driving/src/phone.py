import boto3
import time
import json
import numpy as np
import pickle as pkl
import xgboost as xgb
import threading

class Phone(object):
    def __init__(self):
        self.model = pkl.load(open('../src/xgboost-model', 'rb'))
        self.client = self.create_aws_client('kinesis')
        self.ShardIterator = self.client.get_shard_iterator(
                StreamName='iot-phone-detect',
                ShardId='shardId-000000000000',
                ShardIteratorType='LATEST'
            )['ShardIterator']
        self.is_up = False
    
    def create_aws_client(self, aws_service):
        with open('../aws.json') as aws:
            config = json.load(aws)
            return boto3.client(
                aws_service,
                aws_access_key_id = config['aws_access_key_id'],
                aws_secret_access_key = config['aws_secret_access_key'],
                region_name = config['aws_region']
            )
    
    def check_phone(self):
        return self.is_up

    def run(self):
        while True:
            self.is_up = False
            response = self.client.get_records(
                ShardIterator=self.ShardIterator,
                Limit=1
            )
            if response['Records']:
                data = np.asarray([float(item) for item in str(response['Records'][0]['Data'], encoding='utf-8').strip().split(',')]).reshape(1,15)
                dtest = xgb.DMatrix(data)
                pred = self.model.predict(dtest)
                print(pred)
                if pred > 0.2:
                    self.is_up = True
                else:
                    self.is_up = False
            self.ShardIterator = response["NextShardIterator"]
            time.sleep(1)
