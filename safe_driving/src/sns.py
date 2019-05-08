import json
import boto3
class SNS_subscriber(object):
  '''
  Producer sets up a connection with Amazon Kinesis and sends video frames
  to the server
  '''

  def __init__(self,amazonService='sns'):
    self._sns=self.create_aws_client(amazonService)

  def create_aws_client(self, aws_service):
    with open('../aws.json') as aws:  
      config = json.load(aws)

      return boto3.client(
        aws_service,
        aws_access_key_id = config['aws_access_key_id'],
        aws_secret_access_key = config['aws_secret_access_key'],
        region_name = config['aws_region']
      )
      
      topic_arn = topic['TopicArn']

cli=SNS_subscriber('sns')
#topic = cli._sns.create_topic(Name="SAFE_DRIVING")
#topic_arn = topic['TopicArn']
#print(topic)
    # send!
cli._sns.publish(PhoneNumber='+16462093724',Message="you are falling asleep!")
