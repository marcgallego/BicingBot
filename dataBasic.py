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

def shortestPath(G, d, addresses, bicing):
    addresses = 'Avinguda Diagonal, Carrer Balmes' #JUST FOR TESTING
    coords = addressesTOcoordinates(addresses)
    if(coords == None) return None
    if(G == None) G = creaGraf(d)

    specialNodes = ('source', 'target')
    G.add_nodes_from(specialNodes)
    station_ids = bicing.index.tolist()
    walk_penalizer = 10/4
    for id in station_ids:
        idCoords = getCoords(id)
        distS = haversine(coords[0], idCoords) * walk_penalizer
        distT = haversine(coords[1], idCoords) * walk_penalizer
        G.add_edge(specialNodes[0], id, weight = distS)
        G.add_edge(specialNodes[1], id, weight = distT)

    distST = haversine(coords[0], coords[1]) * walk_penalizer
    G.add_edge(specialNodes[0], specialNodes[1], distST)

    #CALL SHORETEST PATH AND PLOT IT

    G.remove_nodes_from(specialNodes)


def readData():
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index='station_id')
    bicing = bicing.drop(['physical_configuration', 'capacity', 'altitude', 'post_code', 'name', 'address'], axis=1)
    return bicing
bicing = readData()


def getCoords(id, bicing):
    lat = bicing.loc[id, "lat"]
    long = bicing.loc[id, "long"]
    return (lat, long)

def distance(origen, desti):
    coordA = getCoords(origen, bicing)
    coordB = getCoords(desti, bicing)

    r = haversine(coordA, coordB)
    return r

#################################################################################
def creaGraf(max_dist):
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
                distance = distance(origen, desti)
                if (visitat[desti] == False) and (dist <= max_dist):
                    G.add_edge(origen, desti, weight = dist)
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

#Potser estaria be posar aqui dues funcions tontes que diguin edges i nodes (per cohesio)
