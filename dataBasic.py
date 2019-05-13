import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

from pandas import DataFrame
from haversine import haversine
from geopy.geocoders import Nominatim
from staticmap import*



url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
bicing = DataFrame.from_records(pd.read_json(url)['data']['stations'], index='station_id')
station_ids = bicing.index.tolist()

def distancia(d, origen, desti):
    latA = bicing.loc[origen, "lat"]
    lonA = bicing.loc[origen, "lon"]

    latB = bicing.loc[desti, "lat"]
    lonB = bicing.loc[desti, "lon"]

    coordA = (latA, lonA)
    coordB = (latB, lonB)
    r = haversine(coordA, coordB)

    if (r <= d): return True
    else: return False

#################################################################################
def creaGraf(d):
        print('entra')

        G = nx.Graph()
        visitat = dict()

        for id in station_ids:
            G.add_node(id)
            visitat.update({id: False})
        for origen in station_ids:
            visitat[origen] = True;
            for desti in station_ids:
                if (visitat[desti] == False) and (distancia(d, origen, desti) == True):
                    G.add_edge(origen, desti)
        print('graf fet')
        return G

def dibuixaMapa(G):
    print('entra mapa')
    midaX = 500
    midaY = 500
    m = StaticMap(midaX, midaY, url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')

    nodes = list(G.nodes)
    for n in nodes:
        coor = (bicing.loc[n, "lon"], bicing.loc[n, "lat"])
        diametre = int(midaX / 200)
        marker = CircleMarker(coor, 'black', diametre)
        m.add_marker(marker)
    print('nodes fets')

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

    print('arestes fets')

    image = m.render()
    print('render fets')

    image.save('map.png')

    print('mapa fet')

'''
def main():
    G = creaGraf(0.3)
    dibuixaMapa(G)

main()
'''
