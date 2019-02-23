#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import threading

import db_cleanup

class SubwayWatcher(object):
  '''
  Program updates dynamodb with latest data from mta feed every 30 seconds.
  It also cleans up stale entried from db that are over 2 minutes old.
  Usage `python mta_subway_watcher.py`
  '''

  def __init__(self):
    self.db_cleanup_daemon = 'stub'

  def exit_with_msg(self, msg, err):
    '''
    Print message then exit.
    '''
    print ('\n\nProgram Exiting! ' + msg)
    if err:
        print ('Error recieved: {}'.format(err))
    exit(0)

  def run(self):
    try:
      # start DB clean up daemon

      # run update every 30 seconds
      while True:
        print("Fetch update: %s" % time.ctime())
        time.sleep(30)

    except KeyboardInterrupt:
          self.exit_with_msg('Closing MTA Subway Watcher.', None)



if __name__ == '__main__':
    watcher = SubwayWatcher()
    watcher.run() 