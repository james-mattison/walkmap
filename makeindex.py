#!/usr/bin/env python3
import jinja2
import os
import subprocess
import json
from collections import OrderedDict
import re
import time
import argparse

os.chdir("/var/www/html")
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filter", help = "do not filter by minimum length for the most recent", action = "store_true", default = False)
args = parser.parse_args()
# HTML files in this directory. This generates a list of them.
targets = [ file for file in os.listdir("/var/www/html") if file.strip().strip("\n") and ".html" in file ]


def get_tunnel_state():
    s = subprocess.run("ssh -p43000 root@localhost hostname", shell = True)
    if s.returncode == 0:
        return "<font color=\"green\">Connected</font>"
    else:
        return "</font color=\"red\">Disconnected</font>"
def get_web_service_state():
    s = subprocess.run("systemctl is-active gps-web-interface.service --quiet", shell = True)
    if s.returncode == 0:
        return "<font color=\"green\">Running</font>"
    else:
        return "</font color=\"red\">Not Running</font>"

def get_gps_service_state():
    s = subprocess.run("ssh -p43000 root@localhost systemctl is-active gps.service --quiet", shell = True)
    if s.returncode == 0:
        return "<font color=\"green\">Running</font>"
    else:
        return "</font color=\"red\">Not Running</font>"



new_obs = {}
found = False

# for each map file...
for target in targets:
    if "index" in target:
        continue
    # this is the coordinates found in the file.
    # we will use this for length of the distance walked
    # and the sort the maps this
    new_obs[target] = []

    with open (target, "r") as _o:
            blobs = _o.readlines()

    # Thisis where the coordinates start in the map file
    # it is an embedded json array
    for line in blobs:
        # this is the key we want
        if not "path:" in line and not found:
            continue
        if "path:" in line:
            found = True
            continue
        if "]" in line:
            break
        # get everything until the closing bracket
        if found:
            ob = line.strip().lstrip().strip("\n")
            if ob:
                new_obs[target].append(ob)

# sorted, as usual, takes forever to figure out. here is how this works 
#
# key = filter func, ie, [ len(new_obs[key] for key in new_obs ].sort(()
#

#
# print out the html files of the longest -> shortest distance 
# walks measured# 

print(type(new_obs), len(new_obs.keys()))

final = OrderedDict()
f = {}

xkeys = sorted(list(new_obs.keys()), key = lambda key : len(new_obs[key]), reverse = True)

for key in xkeys:
    print("{}: {}".format(key, len(new_obs[key])))

    d = re.findall("[0-9]", key)
    if not d or (len(d) == 1 and not d[0]):
        print(f"Warning: didn't get a good match in key: {key}")
        continue
    ts = int("".join(d))
    t = time.gmtime(ts)
    t = time.strftime("%m-%d-%y %H:%M:%S", t)

    coord_ob = {"num_coords": len(new_obs[key]),
                  "map": key,
                  "date": t,
                  "stamp": ts
                  }

    if not args.filter:
        f[key] = coord_ob
    else:
        if len(new_obs[key]) > 500:
            f[key] = coord_ob

datesort = sorted(f.keys(), key = lambda key : f[key]["stamp"], reverse = True)
print(datesort)
for item in datesort:
    final[item] = f[item]
# { 
#    "html_files": [
#        {
#            "filename": "map-123456",
#            "length": 59344
#        },

with open("/var/www/html/index.html.template", "r") as _o:
    template = jinja2.Template(_o.read())

tunnel_state = get_tunnel_state()
web_service_state = get_web_service_state()
service_state = get_gps_service_state()
geolocation = subprocess.getoutput("ssh -p43000 root@localhost python3 reverse_locate.py").split("\n")[-1]

with open("/var/www/html/index.html", "w") as _o:
    r = template.render(html_files = final, service_state = service_state, web_service_state = web_service_state, tunnel_state = tunnel_state, geolocation = geolocation)
    _o.write(r)
