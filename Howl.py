#!/usr/bin/env python

# Copyright (c) 2011, Peter Hajas
# Additions Copyright (c) 2011, Michael O'Keefe
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted
# provided that the following conditions are met:

# Redistributions of source code must retain the above copyright notice, this list of conditions and
# the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions
# and the following disclaimer in the documentation and/or other materials provided with the
# distribution.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Howl, a parser for Yelp! JSON datasets!

# Howl was designed to run with the Yelp! Academic Dataset: http://www.yelp.com/academic_dataset

# When run, Howl will generate an image and a KML file for a city and state of your choice.
# Or, pass "ALL" as the location, and generate a map of the entire dataset.
#
# $ python Howl.py Troy,NY 1024

# or

# $ python Howl.py ALL 2048

import json
import heatmap
import os, sys
import urllib
import Image
import StringIO
from math import log, exp, tan, atan, pi, ceil

#Google Maps constants
EARTH_RADIUS = 6378137
EQUATOR_CIRCUMFERENCE = 2 * pi * EARTH_RADIUS
INITIAL_RESOLUTION = EQUATOR_CIRCUMFERENCE / 256.0
ORIGIN_SHIFT = EQUATOR_CIRCUMFERENCE / 2.0

#More Google Maps constants
zoom = 15 #this constant changes how many pictures get stitched together
scale = 1
maxsize = 640
bottom = 120

def latlontopixels(lat, lon, zoom):
    mx = (lon * ORIGIN_SHIFT) / 180.0
    my = log(tan((90 + lat) * pi/360.0))/(pi/180.0)
    my = (my * ORIGIN_SHIFT) /180.0
    res = INITIAL_RESOLUTION / (2**zoom)
    px = (mx + ORIGIN_SHIFT) / res
    py = (my + ORIGIN_SHIFT) / res
    return px, py

def pixelstolatlon(px, py, zoom):
    res = INITIAL_RESOLUTION / (2**zoom)
    mx = px * res - ORIGIN_SHIFT
    my = py * res - ORIGIN_SHIFT
    lat = (my / ORIGIN_SHIFT) * 180.0
    lat = 180 / pi * (2*atan(exp(lat*pi/180.0)) - pi/2.0)
    lon = (mx / ORIGIN_SHIFT) * 180.0
    return lat, lon

if len(sys.argv) < 4:
    print "Howl, a parser for Yelp! JSON datasets!\nHowl will generate an image and a KML file for a city of your choice.\nAlternatively, pass \"ALL\" as the location for a map of all points.\n\nUsage: howl.py [City,State] [Output Image Width] [Yelp! Dataset Path]"
    quit()

city = state = None

# If they passed us a city and state (and not ALL), parse them out

location = sys.argv[1]
locationTuple = location.split(",")

if len(locationTuple) == 2:
    city = locationTuple[0]
    state = locationTuple[1]


# Cast the width to an integer

width = sys.argv[2]
width = int(width)

datasetLocation = sys.argv[3]

# Grab the academic dataset

yelpFile = open(datasetLocation)

points = [ ]

# Keep track of minimum and maximum latitude / longitude for scaling

minLatitude = 91
maxLatitude = -91

minLongitude = 181
maxLongitude = -181

for line in yelpFile:
    data = json.loads(line)
    if data["type"] == "business":
        if location == "ALL" or (data["city"] == city and data["state"] == state) or (data["state"] == location):
            # Save the point
            latitude = data["latitude"]
            longitude = data["longitude"]
            
            point = (longitude, latitude)
            
            # Append it to our points list for how many star ratings the place has
            stars = data["stars"]
            
            for i in range(0, int(stars)):
                points.append(point)
            
            # Calculate minimum/maximum latitude/longitude
            
            if latitude < minLatitude:
                minLatitude = latitude
            if latitude > maxLatitude:
                maxLatitude = latitude
            
            if longitude < minLongitude:
                minLongitude = longitude
            if longitude > maxLongitude:
                maxLongitude = longitude

# If we didn't find any points, let's let them know

if len(points) == 0:
    print "No points for {0}, {1}".format(city, state)
    quit()

# Do some stuff to get a google maps image
ulx, uly = latlontopixels(maxLatitude, minLongitude, zoom)
lrx, lry = latlontopixels(minLatitude, maxLongitude, zoom)

dx = ceil(lrx - ulx)
dy = ceil(uly - lry)

cols, rows = int(ceil(dx/maxsize)), int(ceil(dy/maxsize))

largura = int(ceil(dx/cols))
altura = int(ceil(dy/rows))
alturaplus = altura + bottom

final = Image.new("RGB", (int(dx), int(dy)))

for x in range(cols):
    for y in range(rows):
        dxn = largura * (0.5 + x)
        dyn = altura * (0.5 + y)
        latn, lonn = pixelstolatlon(ulx + dxn, uly - dyn - bottom/2, zoom)
        position = ','.join((str(latn), str(lonn)))
	#Uncomment the line below to get Google Maps position updating statements        
	#print x, y, position
        urlparams = urllib.urlencode({'center': position,
                                      'zoom': str(zoom),
                                      'size': '%dx%d' % (largura, alturaplus),
                                      'maptype': 'satellite',
                                      'sensor': 'false',
                                      'scale': scale})
        url = 'http://maps.google.com/maps/api/staticmap?' + urlparams
        f=urllib.urlopen(url)
        im=Image.open(StringIO.StringIO(f.read()))
        final.paste(im, (int(x*largura), int(y*altura)))

# Compute dimensions such that we can have an image with the right aspect ratio

longitudeDifference = maxLongitude - minLongitude
latitudeDifference = maxLatitude - minLatitude

width = int(dx)
height = int(dy)
#scaleFactor = width / longitudeDifference

#height = int(scaleFactor * latitudeDifference)

# Now, ask heatmap to create a heatmap

hm = heatmap.Heatmap()

# Save the heatmap as a PNG, KML and a PNG with Google Maps file

outputName = location

hm.heatmap(points, outputName +"nomap.png", 30, 200, (width,height), scheme='classic')
hm.saveKML(outputName + ".kml")

ima = Image.open(outputName + ".png")
final.paste(ima, None, ima)

final.save(outputName + "map.png")
