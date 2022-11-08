import gmplot
import json
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("infile", action = "store")
parser.add_argument("outfile", action = "store")

def make_plot(blob, outfile):
    lats = []
    lons = []

    for coord in blob['coordinates']:
        if 'lat' in coord.keys() and 'lon' in coord.keys():
            lats.append(float(coord['lat']))
            lons.append(float(coord['lon']))

    plotter = gmplot.GoogleMapPlotter(lats[0], lons[0], 13)

    plotter.plot(lats, lons, 'red', edge_width = 3)
    plotter.apikey = os.environ['GMAP_API_KEY']

    plotter.draw(outfile)

    print(f"Wrote {outfile}")

if __name__ == "__main__":
    args = parser.parse_args()
    with open(args.infile, "r") as _o:
        ob = json.load(_o)
    make_plot(ob, args.outfile)
