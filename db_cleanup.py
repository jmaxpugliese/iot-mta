#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import threading

class DbCleanup(threading.Thread):

  def run(self):
    # run cleanup every 120 seconds
    while True:
      print("Cleanup database: %s" % time.ctime())
      time.sleep(120)