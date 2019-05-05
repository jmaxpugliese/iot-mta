from __future__ import print_function
import time, sys, signal, atexit
from upm import pyupm_mma7660 as upmMMA7660
import boto
import json
KINESIS_STREAM_NAME = 'acceleration'
ACCOUNT_ID = '951091509964'
IDENTITY_POOL_ID = 'us-east-1:f2fca7ca-fbc7-4e6c-80ef-5ba1be2c3cad'
ROLE_ARN = 'arn:aws:iam::951091509964:role/Cognito_edisonDemoKinesisUnauth_Role'
def get_acceleration():
    # Instantiate an MMA7660 on I2C bus 0
    myDigitalAccelerometer = upmMMA7660.MMA7660(
                                            upmMMA7660.MMA7660_DEFAULT_I2C_BUS,
                                            upmMMA7660.MMA7660_DEFAULT_I2C_ADDR);    
    # place device in standby mode so we can write registers
    myDigitalAccelerometer.setModeStandby()
    # enable 64 samples per second
    myDigitalAccelerometer.setSampleRate(upmMMA7660.MMA7660_AUTOSLEEP_64)
    # place device into active mode
    myDigitalAccelerometer.setModeActive()
    return myDigitalAccelerometer
'''
## Exit handlers ##
    # This function stops python from printing a stacktrace when you hit control-C
def SIGINTHandler(signum, frame):
        raise SystemExit

    # This function lets you run code on exit, including functions from myDigitalAccelerometer
def exitHandler():
        print("Exiting")
        sys.exit(0)

    # Register exit handlers
atexit.register(exitHandler)
signal.signal(signal.SIGINT, SIGINTHandler)
'''

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
# create a stream with 1 shards
#stream_kinesis = client_kinesis.create_stream(KINESIS_STREAM_NAME, 1)
#print('Creating stream...')
#time.sleep(20)


myDigitalAccelerometer=get_acceleration()
ax = upmMMA7660.new_floatp()
ay = upmMMA7660.new_floatp()
az = upmMMA7660.new_floatp()
for i in range(25):
  myDigitalAccelerometer.getAcceleration(ax,ay,az)
  outputStr = ("Acceleration: x = {0}"
                     "g y = {1}"
                     "g z = {2}g").format(upmMMA7660.floatp_value(ax),
        upmMMA7660.floatp_value(ay),
        upmMMA7660.floatp_value(az))
  record = {'Time': time.time(), 'ax': upmMMA7660.floatp_value(ax),'ay':upmMMA7660.floatp_value(ay),'az':upmMMA7660.floatp_value(az)}
# write data into the stream
  client_kinesis.put_record(KINESIS_STREAM_NAME,json.dumps(record),'acceleration')
  print(outputStr)
  time.sleep(1)