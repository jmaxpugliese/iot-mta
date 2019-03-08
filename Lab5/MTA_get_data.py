import sys
import time
import datetime
import json

sys.path.append('./utils')
from mta_updates import MTAUpdates


def mta_get_data():
    mta_updater = MTAUpdates()
    mta_updater.update()

    res = [json.dumps(mta_updater.trip_updates[key].to_json(), sort_keys=True, indent=4, separators=(',', ': ')) + ',\n' for key in mta_updater.trip_updates]
    with open(filepath, 'a') as file:
        file.writelines(res)
    print('write!')
    time.sleep(20)


if __name__ == '__main__':
    filepath = './mataData-{}.json'.format(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
    with open(filepath, 'w') as file:
        file.write('[\n')
    try:
            while True:
                mta_get_data()
    except KeyboardInterrupt:
        with open(filepath, 'a') as file:
            file.write(']\n')
        exit
