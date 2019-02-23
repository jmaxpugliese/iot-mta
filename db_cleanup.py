#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import threading

class DbCleanup(threading.Thread):

  def run(self):
    # run cleanup every 120 seconds
    while True:
      print("Cleanup database: %s" % time.ctime())
      delete_stale_data()
      time.sleep(120)

  def delete_stale_data(self):
    # conntect to database

    # delete data with timestamp prior to current time - 120s