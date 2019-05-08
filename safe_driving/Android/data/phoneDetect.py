import boto3
import time
import numpy as np
import pickle as pkl
import xgboost as xgb
import threading

class phone_detect:
    def __init__(self):
        self.model = pkl.load(open('xgboost-model', 'rb'))
        self.client = boto3.client('kinesis')
        self.ShardIterator = self.client.get_shard_iterator(
                StreamName='iot-phone-detect',
                ShardId='shardId-000000000000',
                ShardIteratorType='LATEST'
            )['ShardIterator']
        self.is_up = False

    def check_phone(self):
        return self.is_up

    def run(self):
        while True:
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

if __name__ == '__main__':
    phone = phone_detect()
    t1 = threading.Thread(target=phone.run)
    t1.start()