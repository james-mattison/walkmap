#!/usr/bin/env python3
import serial
import atexit
import lib.controllers.lcdprint as lcdprint 
from datetime import datetime
import os
import time
import pynmea2
import subprocess
import json

# LED module
import lib.controllers.led as led

# global leds
green = led.Green()
red = led.Red()
blue = led.Blue()

atexit.register(led.GPIO.cleanup)
for _led in [ red, green, blue ]:
    _led.off()

def on(*colors):
    for color in colors:
        color.on()


def off(*colors):
    for color in colors:
        color.off()

def blink(*colors):
    for color in colors:
        color.blink()

def get_start():
    i_start = int(time.time())
    start = datetime.now().strftime("%m-%d-%y %H:%M:%S")
    return {"i_start": i_start, "start": start}

old_file = f"/root/history/gps-{str(int(time.time()))}.json"

def mv():
    subprocess.run(f"cp /root/gps.json {old_file}", shell = True)
    try: 
        #o = subprocess.run(f"python3 /root/write_map.py {old_file} &", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        with open("/root/gps.py", "w") as _out:
            json.dump({
                "coordinates": []
                }, _out, indent = 4)
        print("Starting gps.json")
       # print(o.stdout.decode(errors = 'ignore'))
        print(f"Moved initial file")
        lcdprint.saything("WROTE HISTORY FILE")
    except Exception as e:
        print(e)
        lcdprint.saything("HIST FILE NOT WRITTEN")
    time.sleep(2)

def load():
    if not os.path.exists("/root/gps.json"):
        with open("/root/gps.json", "w") as _o:
            ob = {"coordinates": []}
            for k, v in get_start().items():
                ob[k] = v
            json.dump(ob, _o, indent = 4)
            print("Started initial gps.json")
            return ob
    else:
        with open("/root/gps.json", "r") as _o:
            try:
                js = json.load(_o)
                if not isinstance(js, dict) or not js.get('coordinates'):
                    print(f"Missing key 'coordinates' in gps.json. Overwriting.")
                    js = {"coordinates": []}
                    for k, v in get_start().items():
                        js[k] = v
                return js
            except json.JSONDecodeError as e:
                print(e)
                print("Got bogus JSON decode for gps.json. Overwriting.")
                with open("/root/gps.json", "w") as _o:
                    js = {"coordinates": []}
                    for k, v in get_start().items():
                        js[k] = v
                    json.dump(js, _o, indent = 4)
                return js



def stepiter():
    while True:
        s = "-/|\\-"
        for i in s:
            yield i
                    

def dump(new_js):
    js = load()
    if not js:
        print("Got bullshit back from call to load()")
        js = { "coordinates": [] }
    for k, v in get_start().items():
        js[k] = v 

    js['coordinates'].append(new_js)
    with open("/root/gps.json", "w") as _o:
        json.dump(js, _o, indent = 4)
    print(f"- dumped gps.json")



if __name__ == "__main__": 

    lcdprint.saything("GPS SYSTEM BOOT:", datetime.now().strftime("%H:%M:%S"))
    ser = serial.Serial("/dev/ttyAMA0", baudrate = 9600, timeout = 0.5)

    datareader = pynmea2.NMEAStreamReader()

    fired = False

    off(red, green, blue)

    for light in [red, green, blue]:
        on(light)
        time.sleep(1)

    it = stepiter()
    i = 0 
    mv()

    start = int(time.time())
    on(red)
    started = False
    while True:
        if i % 25 == 0 and i != 0:
            blob = load()
            if blob['coordinates'][-1].get('failed'):
                lcdprint.saything("STATE: FAILED")
                off(green, blue)
                on(red)

            else:
                now = int(time.time())
                st = f"STATE: RUNNING", f"{now-start}s"
                lcdprint.saything("STATE: RUNNING", f"{int(now-start)}s")
                on(green)
                off(red, blue)
            
            time.sleep(5)
            i += 1
        data = ser.readline().decode(errors = 'ignore')

        if not data:
            lcdprint.saything("NOT CONNECT", "NO PAYLOAD")
            on(red)
            off(blue, green)
            time.sleep(1)
            continue

        if not fired and not data:
            lcdprint.saything("BOOTING", next(it))
            time.sleep(1)
            on(blue)
            off(green, red)
            continue

        if data and not "$GPRMC" in data and not fired:
            lcdprint.saything("SATELLITE CONNECTED. AWAIT DATA.")
            blink(blue, green)
            time.sleep(1)
            continue

        elif "$GPRMC" in data:
            fired = True
            try:
                msg = pynmea2.parse(data)
            except pynmea2.nmea.ParseError as e:
                lcdprint.saything("NMEA PARSE ERROR", "RETRYING...")
                on(red)
                off(green, blue)
                blink(red)
                time.sleep(1)
                blink(red)
                dump({"failed": True, "when": "[" + datetime.now().strftime("%H:%M:%S") + "]",
                      "why": "Could not parse NMEA line.",
                      "index": i,
                      "bad_line": data
                      })
                continue
            if (not msg.latitude or not msg.longitude) and not started:
                lcdprint.saything(f"DATA READ FAIL", "NO SAT CONN")
                dump({
                    "failed": True,
                    "when": "[" + datetime.now().strftime("%H:%M:%S") + "] OFFLINE",
                    "why": "Couldn't read data.",
                    "index": i
                    }
                )
                i += 1
                off(blue, green)
                on(red)
                blink(red)
                time.sleep(1)
                blink(red)
                continue
            if msg.latitude == 0.0 or msg.longitude == 0.0 and started:
                lcdprint.saything("DATA READ FAIL", "NOT CONNECT")
                off(blue, green)
                on(red)
                blink(red)
                time.sleep(1)
                blink(red)
                continue

            # removed else:
            lat = str(msg.latitude)[:12]
            lon = str(msg.longitude)[:12]
            lcdprint.saything(f"LAT: {lat}", f"LON: {lon}")
            dump({"when": datetime.now().strftime("%H:%M:%S"),
                "index": i,
                "failed": False,
                "why": "Connected to sat",
                "lat": lat,
                "lon": lon
                })
            off(red, blue)
            on(green)
            if i % 10 == 0:
                green.blink()
            started = True
            time.sleep(1)
            i += 1

