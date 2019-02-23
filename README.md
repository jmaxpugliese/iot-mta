## 1. Instructions for installing on a fresh VM

A. Install pip:
`sudo apt-get install python-pip`

B. Install Python virtual environment: `pip install --upgrade virtualenv`

C. Create new Python project: `virtualenv <dir>`

D. Navigate to newly created directory: `cd <dir>`

E. Activate virtual environment: `source bin/activate`

Mac install GTFS
curl -O https://developers.google.com/transit/gtfs-realtime/gtfs-realtime.proto
curl -O http://datamine.mta.info/sites/all/files/pdfs/nyct-subway.proto.txt && mv nyct-subway.proto.txt nyct-subway.proto

brew install protobuf
protoc -I=. --python_out=. *.proto