Howl, a visualizer for the Yelp! academic dataset
=================================================

by Peter Hajas and Michael O'Keefe

![Troy, NY as visualized by Howl](http://i.imgur.com/CTOmS.png "Troy, NY")

(Troy, NY as visualized by Howl)

![Troy, NY as visualized by Howl with Google Maps underlay](http://i.imgur.com/vqYvBl.png "Troy, NY With Map")

(Troy, NY as visualized by Howl with Google Maps underlay)

About
-----

Howl is a simple python tool for visualizing location reviews around your town.

The more red/white a point is, the better the reviews.

Howl requires Heatmap.py, the Python Image Library and a recent Python version.

Howl was designed for use with the [Yelp! Academic Dataset](http://www.yelp.com/academic_dataset)

Usage
-----

Simply run Howl with a city, state and an image width

`./Howl.py Troy,NY 1024 yelp_academic_dataset.json`

or with ALL as a location, to generate an image for the entire dataset:

`./Howl.py ALL 1024 yelp_academic_dataset.json`
(this will probably take a while)

You can also run Howl with just the state:
`./Howl.py NY 1024 yelp_academic_dataset.json`

If you want to specify the Google Maps type, you can do so after the yelp dataset location:
`./Howl.py NY 1024 yelp_academic_dataset.json roadmap`

The options are `roadmap` `satellite` `terrain` or `hybrid`.

Howl will generate images and KML file for your location. It'll save them in the current working directory, like this:

`Troy,NY_nomap.png`, `Troy,NY_map.png`, `Troy,NY.kml` or `ALL.png`

Where the nomap files have no Google Maps underlay, and the map files do.

Open Howl KML files in a tool like Google Earth to visualize reviews.


It's really neat!

Legal
-----

Howl is Copyright 2011 Peter Hajas and Michael O'Keefe. It's BSD licensed. The full text of the license can be found in Howl.py.

The work in Howl does not imply endorsement by past, current or future
employers.
