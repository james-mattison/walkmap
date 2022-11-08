import googlemaps
import json
import argparse

parser  = argparse.ArgumentParser()
parser.add_argument("gps_file", action = "store", nargs = "?")
parser.add_argument("-a", "--latitude", action = "store")
parser.add_argument("-o", "--longitude", action = "store")
args = parser.parse_args()

failed = False

if not args.gps_file:
    if not args.latitude:
        print("Missing -a/--latitude since no gps_file was specified.")
        failed = True
    if not args.longitude: 
        print("Missing -o/--longitude since no gps_file was specified.")
        failed = True
if failed:
    print("Failed")
    quit(1)
if args.gps_file:
    with open(args.gps_file, "r") as _o:
        js = json.load(_o)
    last = js['coordinates'][-1]
else:
    last = { "lon": float(args.longitude), "lat": float(args.latitude)}
    


lon = str("{:07f}".format(float(last['lon'])))

lat = str("{:07f}".format(float(last['lat'])))

gmaps = googlemaps.Client(api_key)

gr = gmaps.reverse_geocode((lat, lon))

best_guess = gr[0].get("formatted_address")
if best_guess:
    best_guess = best_guess.replace(',', '\n')
js['coordinates'][-1]['best_guess'] = best_guess

with open("/var/log/syslog", "a") as _log:
    with open(args.gps_file, "w") as _o:
        json.dump(js, _o, indent = 4)
        print(f"Dumped {args.gps_file}", file = _log)

    print(f"***GPS WRITEOUT***\nBest guess:\n{best_guess}\n******************", file = _log)

print(f"Best guess:\n {best_guess}") 

