#!/usr/bin/env python3
import serial
import atexit
import lcdprint
from datetime import datetime
import os
import time
import pynmea2
import subprocess
import json
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except ImportError as e:
    print("DEV MODE - no RPi.GPIO!")
    GPIO = None



##
## LED: Configure the RGP LED light
##

class LED:
    """
    Methods to configure 4-post RGP LED."""

    def __init__(self, pin: int):
        self.pin = pin
        if GPIO:
            GPIO.setup(self.pin, GPIO.OUT)

    def on(self):
        if GPIO:
            GPIO.output(self.pin, True)
        else:
            print(f"ON {self.__class__.__name__}")

    def off(self):
        if GPIO:
            GPIO.output(self.pin, False)
        else:
            print(f"OFF {self.__class__.__name__}")

    def blink(self):
        time.sleep(0.1)
        self.on()
        time.sleep(0.1)
        self.off()

class Blue(LED):

    def __init__(self):
        super().__init__(26)

class Red(LED):

    def __init__(self):
        super().__init__(13)

class Green(LED):

    def __init__(self):
        super().__init__(19)

##
##  gps.json methods
##

class GPSFile:

    @staticmethod
    def timestamp():
        return {
            "i_start": int(time.time()),
            "start": datetime.now().strftime("%m-%d-%y %H:%M:%S")
        }

    def __init__(self):
        self.gps_file = "gps.json"
        self.data = {
            "coordinates": [],
            "start": None,
            "epoch_start": None
        }

    def _dump(self, data: dict, file: str = None):
        if not file:
            file = self.gps_file

        with open(file, "w") as _o:
            json.dump(data, _o, indent = 4)

    def _load(self, file: str = None):
        if not file:
            file = self.gps_file

        with open(file, "r") as _o:
            try:
                js = json.load(_o)
            except json.JSONDecodeError as e:
                blob = _o.read()
                rev = reversed(blob)
                rev.


        stamp = self.timestamp()

        js = {**js, **stamp}

        return js
