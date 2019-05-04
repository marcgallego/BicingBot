import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

from pandas import DataFrame
from haversine import haversine
from geopy.geocoders import Nominatim
from staticmap import*


from dataFrame import creaGraf, bicing

def dibuixaMapa():
    G = nx.Graph()
    creaGraf(G)
    midaX = 2500
    midaY = 2500
    m = StaticMap(midaX, midaY, url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')

    nodes = list(G.nodes)
    for n in nodes:
        coor = (bicing.loc[n, "lon"], bicing.loc[n, "lat"])
        diametre = int(midaX / 200)
        marker = CircleMarker(coor, 'black', diametre)
        m.add_marker(marker)

    edges = list(G.edges.data())
    gruix = int(midaX / 300)
    for e in edges:
        origen = e[0]
        desti = e[1]

        latA = bicing.loc[origen, "lat"]
        lonA = bicing.loc[origen, "lon"]

        latB = bicing.loc[desti, "lat"]
        lonB = bicing.loc[desti, "lon"]

        coorA = (lonA, latA)
        coorB = (lonB, latB)
        m.add_line(Line(((coorA), (coorB)), 'blue', gruix))


    image = m.render()
    image.save('map.png')
    print('mapa fet')
    import os


def main():
    dibuixaMapa()
    statinfo = os.stat('map.png')
    if(statinfo.st_size >= 10000000):
        print('Massa gran: ', statinfo.st_size/1000000, 'MB')
    else:
        print('Mida correcte: ', statinfo.st_size/1000000, 'MB')

main()
