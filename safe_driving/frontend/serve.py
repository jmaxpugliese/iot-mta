#!/usr/bin/env python

from flask import Flask, jsonify, request, render_template
import time, threading, random, webbrowser
import sys

sys.path.append("../src")
from consumer import Consumer
from phone import Phone

app = Flask(__name__)

monitor = Consumer()
phone = Phone()

warning = False
Eye_Close_Count = 0
Looking_Away_Count = 0

@app.route("/monitor", methods=['GET'])
def data():
    global warning, Eye_Close_Count, Looking_Away_Count
    warning = False
    """
    Primary data source for AJAX/REST queries. Gets the server's current
    time two ways: as raw data, and as a formatted string. NB While other
    Python JSON emitters will directly encode arrays and other data types,
    Flask.jsonify() appears to require a dict.
    """
    driver_info = monitor.get_info()
    phone_up = phone.check_phone()

    if not driver_info['eye']:
        Eye_Close_Count += 1
    else:
        Eye_Close_Count = 0
    if not driver_info['head']:
        Looking_Away_Count += 1
    else:
        Looking_Away_Count = 0

    if phone_up or Eye_Close_Count >= 3 or Looking_Away_Count >= 3:
        warning = True

    info = {
        'Eye_Open':         driver_info['eye'],
        'Looking_Forward':  driver_info['head'],
        'Phone_Up':         phone_up,
        'Warning':          warning
    }
    
    return jsonify(info)


@app.route("/updated")
def updated():
    """
    Wait until something has changed, and report it. Python has *meh* support
    for threading, as witnessed by the umpteen solutions to this problem (e.g.
    Twisted, gevent, Stackless Python, etc). Here we use a simple check-sleep
    loop to wait for an update. app.config is handy place to stow global app
    data.
    """
    while not app.config['updated']:
        time.sleep(0.5)
    app.config['updated'] = False    # it'll be reported by return, so turn off signal
    return "changed!"


@app.route("/")
def main():
    return render_template("index.html")


def occasional_update(delay = 0.5, first_time=False):
    """
    Simulate the server having occasional updates for the client. The first
    time it's run (presumably synchronously with the main program), it just
    kicks off an asynchronous Timer. Subsequent invocations (via Timer)
    actually signal an update is ready.
    """
    app.config['updated'] = not first_time
    threading.Timer(delay, occasional_update).start()


if __name__ == "__main__":
    # start occasional update simulation
    occasional_update(first_time=True)

    threading.Thread(target = monitor.run).start()
    threading.Thread(target = phone.run).start()
    
    # consumer process the video frames
    # consumer.run()

    # start server and web page pointing to it
    port = 5000 + random.randint(0, 999)
    url = "http://127.0.0.1:{}".format(port)
    wb = webbrowser.get(None)  # instead of None, can be "firefox" etc
    threading.Timer(1.25, lambda: wb.open(url) ).start()
    app.run(port=port, debug=False)
