## 1. Instructions for installing on a fresh VM

A. Install pip:
`sudo apt-get install python-pip`

B. Install Python virtual environment: `pip install --upgrade virtualenv`

C. Create new Python project: `virtualenv <dir>`

D. Navigate to newly created directory: `cd <dir>`

E. Activate virtual environment: `source bin/activate`

F. Install World Timezone information: `pip install pytz`

G. Install World Timezone information: `pip install boto3`

H. For Lab 6: `pip install django`
  - Launch the web server by running: `python manage.py runserver <your ip address>:<port number>`

/*******************************************************************************/

a. Steps to inswtall protobuf on Mac:

curl -O https://developers.google.com/transit/gtfs-realtime/gtfs-realtime.proto

curl -O http://datamine.mta.info/sites/all/files/pdfs/nyct-subway.proto.txt && mv nyct-subway.proto.txt nyct-subway.proto

brew install protobuf

b. Steps to inswtall protobuf on Linux:

wget https://developers.google.com/transit/gtfs-realtime/gtfs-realtime.proto

wget http://datamine.mta.info/sites/all/files/pdfs/nyct-subway.proto.txt && mv nyct-subway.proto.txt nyct-subway.proto

sudo apt install protobuf-compiler

/*******************************************************************************/

protoc -I=. --python_out=. *.proto
