"""Read input data and define helper functions for visualization."""
import json

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from collections import deque

# Map services and data available from U.S. Geological Survey, National Geospatial Program.
# Please go to http://www.usgs.gov/visual-id/credit_usgs.html for further information
united_states_map = mpimg.imread("map.png")  # US States & Capitals map

# List of 30 US state capitals and corresponding coordinates on the map
with open('capitals.json', 'r') as capitals_file:
    capitals = json.load(capitals_file)
capitals_list = [(k, tuple(v)) for k, v in capitals.items()]

def show_path(path, starting_city, w=12, h=8):
    """Plot a TSP path overlaid on a map of the US States & their capitals."""
    x, y = list(zip(*path))
    _, (x0, y0) = starting_city
    plt.imshow(united_states_map)
    plt.plot(x0, y0, 'y*', markersize=15)  # y* = yellow star for starting point
    plt.plot(x + x[:1], y + y[:1])  # include the starting point at the end of path
    plt.axis("off")
    fig = plt.gcf()
    fig.set_size_inches([w, h])
    
def contains(paths, x):
    """Test whether a path equivalent to x (rotated or reversed) exists in the paths list"""
    x = deque(x)
    for _ in range(len(x)):
        x.rotate(1)
        path = tuple(x)
        if path in paths or path[::-1] in paths: return True
    return False
