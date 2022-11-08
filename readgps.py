#!/usr/bin/env python

import csv
import os
import argparse
import gmplot
import subprocess
import json
import time
import getpass
from led import LED, DummyLed
import flask

"""
readgps.py: tools to read and render geolocation data using the Google Maps API.

This script is specifically intended to allow you to take the data from GPSLogger, on
an androind phone, and load it into a usable and parse-able format.

Running this program should check that the mount specified is valid, contains files,
and then uses csv to load the files into a DictReader.

Also, the GPSData class contains an important method, make_map_html_file, which will
return a fully rendered HTML webpage of the data.

Requires additional library 'gmplot' : https://pypi.org/project/gmplot/
"""
os.chdir("/root")
app = flask.Flask(__name__)

os.environ['GMAP_API_KEY']
LOCAL_DATA_DIR="/mnt/gpsdata"
REMOTE_DATA_DIR="/sdcard/GPSLogger"
WORKING_DIR="/root/gpsdata"
MANIFEST_FILE="/mnt/gpsdata/manifest.json"


parser = argparse.ArgumentParser()

# This is expected to be one of the files that GPSLogger outputs, ie,
parser.add_argument("infile", help = "file to read")
parser.add_argument("-o", "--outfile", action = "store", default = "map.html")
parser.add_argument("-d", "--dryrun", action = "store_true", default = False)
# load all the files on the sd card and render them, making index.html too
# This is the flag that the daemon uses
parser.add_argument("-a", "--all", action = "store_true", default = False)

### Helper func: run, run commands on this host
def run(cmd: str, die_on_fail: bool = False, get_object: bool = False):
    r = subprocess.run(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if r.returncode != 0 and die_on_fail:
        raise Exception("Bad return from %s" % cmd)
    o = r.stdout.decode(errors = 'ignore')
    #print(o)
    return r if get_object else o

class DataCollector:
    """
    Methods to acquire the data from an Android phone running GPSLogger

    TODO: make this more generic and less crap
    """

    @classmethod
    def check_new_data(cls) -> list:
        # TODO AGNOSTICIZE PATHS
        new_files = []

        # Load the manifest, a list of files this script has already generated
        # the HTML pages for. This is the thign we compare against to determine if new
        # files are required.
        with open(MANIFEST_FILE, "r") as _o:
            current_files = json.load(_o)

        n = 0
        # TODO: Genericize
        for file in os.listdir(LOCAL_DATA_DIR):
            if not "AppData" in file:
                n = n + 1
                print("{}: Processing file:  {} \r".format(n, file), end = "", flush = True)
                subprocess.run(f"cp {LOCAL_DATA_DIR}/{file} {WORKING_DIR}/", shell = True)
                new_files.append(file)

        # Update the manifest
        with open(MANIFEST_FILE,  "w") as _o:
            json.dump(current_files + new_files, _o, indent = 4, sort_keys = False)
        print()

        # return the DIFF
        return new_files

class GPSData:
    """
    Tools to deal with loading a CSV-formatted file containing GPS information
    """

    # TODO: make this a less confusing var name or get rid of
    index_lines = []

    @classmethod
    def from_file(cls, filename) -> csv.DictReader:
        # Load a file, returning a csv.DictReader
        # todo, make this a proper classmethod
        filename = os.path.join(WORKING_DIR, filename)
        # open fd to filename
        f = open(filename, "r")
        reader = csv.DictReader(f)

        return cls(reader)

    def __init__(self, reader: csv.DictReader):
        self.reader = reader

    def get_key(self, *keys) -> list:
        """
        Iterate through each line in the given CSV formatted file, returning a
        list of dictionaries; the keys of these dicts will be *keys.
        """

        got = []

        for line in self.reader:
            # create a dict from this line consisiting of k:v pairings, where k is *keys
            o = {}
            for key, value in line.items():
                if key in keys:
                    o[key] = value
                    got.append(o)
        #print(f"Total {len(got)} keys read.")
        return got

    def get_keys(self, *keys) -> list:
        """ Alias for get_key above """
        return self.get_key(*keys)

    def get_lat_lon(self) -> tuple:
        """ Somewhat ugly way of itering over values from get_key for latitutde, longitude."""
        str_keys = self.get_key("latitude", "longitude")
        lats = []
        lons = []
        for item in str_keys:
            o = float(item.get("latitude"))
            u = float(item.get("longitude"))
            lats.append(o)
            lons.append(u)

        # Returns a tuple, (lats, lons)
        return lats, lons

    def make_map_html_file(self, filename = "/var/www/html/map.html", it = None, limit = 500) -> None:
        # Todo: genericize
        lat, lon = self.get_lat_lon()

        if len(lat) < limit:
            return False

        # Todo: parameterize the creation of the plotter
        # Constuctor takes:
        # - lat
        # - lon
        #  - The zoom of the actual map itself. default 13.
        gmap = gmplot.GoogleMapPlotter(lat[0], lon[0], 13)

        # Do the thing whatfor it draws a line through all the places
        # that the GPS data marks itself as having been to.

        # a short guide to args for gmap's `plot` constructor, in order:
        #  -> seq(lat), eg an unpacked iterable ( *lat vs lat ) of
        #     latitudes as floats
        #  -> seq(lon), eg an unpacked iterable of longitutes as floats
        #  -> str(line_color), ie 'blue', or '\#FF0000'
        #  -> edge_width -> thickness of the line between the points. 6 is good.
        gmap.plot(lat, lon, 'red', edge_width = 3)

        gmap.apikey = API_KEY

        # render the map into an HTML file. counts as a call against the google
        # maps API
        gmap.draw(filename)

        # todo: confusing var name
        # append a link to the generated file to the rendered index.html
        self.index_lines.append(filename)
        print(f"{it} Wrote map to {filename}\r", end = "", flush = True)

    @classmethod
    def write_index(cls):
        # Todo: use a dang jinja template here my goodness
        # >:-(

        s = "<html><head></head><body><h4>Walk Maps</h4>"
        for file in sorted(os.listdir("/var/www/html")):
            if file.endswith(".html") and file != "index.html":
                s += f'<br><a href="{file}">{file}</a>'
                e = "</body></html>"
        with open("/var/www/html/index.html", "w") as _o:
            _o.write("\n".join([s, e]))
@app.route("/img/<imgname>", methods = [ "get", "post" ])
def render_images(imgname):
    if imgname in os.listdir("static"):
        return flask.send_from_directory('static', filename = imgname)

@app.route("/map/<mapname>", methods = ["get", "post"])
def render_maps(mapname):
        return flask.send_from_directory('static', filename = mapname)

@app.route("/", methods = ["get", "post"])
def render_index():
    collector = DataCollector()
    targets = os.listdir("static")
    it = 0
    rendered = []
    # And then create google maps for them
    for target in targets:
        o = {}

        if not target.endswith(".html"):
            continue
        html_file = target.split(".")[0]
        fn = html_file + ".html"
        # Load GPS data
        o['href'] = html_file.split("/")[-1] + ".png"
        o['desc'] = "Walk taken on " + html_file
        o['map'] = fn
        rendered.append(o)

    for static_img in [

            "big.png",
            "brother.png",
            "gpspi1.jpg",
            "gpspi2.jpg",
            "is.png",
            "plot.png",
            "walk-to-work.png",
            "watching.png"]:
        rendered.append(
                { "href": static_img, "desc": "Terrifying static image", "map": "#" }
                )

    return flask.render_template("index.html", images = rendered)
if __name__ == "__main__":

    if not getpass.getuser() == "root":
        raise PermissionError("Fatal: must be root.")
    # Get rid of LEDs loleds

    app.run(host = "0.0.0.0", port = 42069)



