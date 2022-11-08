import googlemaps
from datetime import datetime
import os
import json
import time
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("address", action = "store", type = str)

args = parser.parse_args()
gmaps = googlemaps.Client(os.environ.get("GOOGLE_MAPS_API_KEY"))
gr = gmaps.geocode(args.address)

escaped = args.address.replace(",", "").replace(" ", "-")


s = datetime.now().strftime("%m-%d-%y-%H-%M-%S")
with open(f"/root/geolocation_data/geolocate-{escaped}.json", "w") as _o:
    json.dump(gr, _o, indent = 4, sort_keys = False)

for item in gr:
    for k, v in item.items():
        print("{:20}: {:40}".format(k, str(v)))
