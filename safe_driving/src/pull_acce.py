import boto
import json
from datetime import datetime
from pytz import timezone
KINESIS_STREAM_NAME = ''
ACCOUNT_ID = ''
IDENTITY_POOL_ID = ''
ROLE_ARN = ''
#################################################
# Instantiate cognito and obtain security token #
#################################################
# Use cognito to get an identity.
cognito = boto.connect_cognito_identity()
cognito_id = cognito.get_id(ACCOUNT_ID, IDENTITY_POOL_ID)
oidc = cognito.get_open_id_token(cognito_id['IdentityId'])

# Further setup your STS using the code below
sts = boto.connect_sts()
assumedRoleObject = sts.assume_role_with_web_identity(ROLE_ARN, "XX", oidc['Token'])
client_kinesis = boto.connect_kinesis(
    aws_access_key_id=assumedRoleObject.credentials.access_key,
    aws_secret_access_key=assumedRoleObject.credentials.secret_key,
    security_token=assumedRoleObject.credentials.session_token)
TIMEZONE = timezone('America/New_York')

shard_id = 'shardId-000000000000' 
shard_it = client_kinesis.get_shard_iterator(KINESIS_STREAM_NAME, shard_id, "TRIM_HORIZON")["ShardIterator"] 
for i in range(5):
  response = client_kinesis.get_records(shard_it, limit=5) 
  #print(response)
  for o in response["Records"]: 
    acce= json.loads(o['Data']) 
    ax=acce['ax']
    ay=acce['ay']
    az=acce['az']
    timestamp=acce['Time']
    nytime = datetime.fromtimestamp(timestamp,TIMEZONE)
    nytime=str(nytime)[0:19]
    print(nytime+' ax='+str(ax)+'  ay='+str(ay)+'  az='+str(az))
  shard_it = response["NextShardIterator"]

