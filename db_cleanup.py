#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import threading


class DbCleanup(threading.Thread):
    def run(self):
        # run cleanup every 60 seconds
        while True:
            print("Cleanup database: %s" % time.ctime())
            # delete_stale_data()
            time.sleep(60)

    # def delete_stale_data(self):
    #TODO - conntect to aws

    #TODO - delete data with timestamp prior to current time - 60s
