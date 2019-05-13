import pandas as pd
import networkx as nx
import os

from pandas import DataFrame
from haversine import haversine
from geopy.geocoders import Nominatim
from staticmap import *


def addressesTOcoordinates(addresses):
    '''
    Returns the two coordinates of two addresses of Barcelona
    in a single string separated by a comma. In case of failure, returns None.
    '''
    try:
        geolocator = Nominatim(user_agent="bicing_bot")
        address1, address2 = addresses.split(',')
        location1 = geolocator.geocode(address1 + ', Barcelona')
        location2 = geolocator.geocode(address2 + ', Barcelona')
        return (location1.latitude, location1.longitude), (location2.latitude, location2.longitude)
    except:
        return None

def shortestPath(G, d, addresses):
    addresses = 'Avinguda Diagonal, Carrer Balmes'
    coords = addressesTOcoordinates(addresses)
    if(coords == None) return None
    if(G == None) G = creaGraf(d)
    G.add_edge('source')
    for()


def readData():
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index='station_id')
    bicing = bicing.drop(['physical_configuration', 'capacity', 'altitude', 'post_code', 'name', 'address'], axis=1)
    return bicing

def getCoords(id, bicing):
    lat = bicing.loc[id, "lat"]
    long = bicing.loc[id, "long"]
    return (lat, long)

bicing, station_ids = readData()

def distancia(d, origen, desti):
    coordA = getCoords(origen, bicing)
    coordB = getCoords(desti, bicing)

    r = haversine(coordA, coordB)

    if (r <= d): return True
    else: return False

#################################################################################
def creaGraf(d):
        print('entra')

        G = nx.Graph()
        visitat = dict()
        station_ids = bicing.index.tolist()

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
    midaX, midaY = 500
    m = StaticMap(midaX, midaY, url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')

    nodes = list(G.nodes)
    for n in nodes:
        coor = getCoords(n, bicing)
        diametre = int(midaX / 200)
        marker = CircleMarker(coor, 'black', diametre)
        m.add_marker(marker)
    print('nodes fets')

    edges = list(G.edges.data())
    gruix = int(midaX / 300)
    for e in edges:
        origen = e[0]
        desti = e[1]

        coorA = getCoords(origen, bicing)
        coorB = getCoords(desti, bicing)
        m.add_line(Line(((coorA), (coorB)), 'blue', gruix))

    print('arestes fets')

    image = m.render()
    print('render fets')

    image.save('map.png')

    print('mapa fet')

def connectedComponents(G):
    return number_connected_components(G)


'''
def main():
    G = creaGraf(0.3)
    dibuixaMapa(G)
main()
'''
