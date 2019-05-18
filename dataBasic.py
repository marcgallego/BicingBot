import pandas as pd
import networkx as nx
import os

from pandas import DataFrame, Series
from haversine import haversine

from geopy.geocoders import Nominatim
from staticmap import *



def readData():
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index='station_id')
    bicing = bicing.drop(['physical_configuration', 'capacity', 'altitude', 'post_code', 'name', 'cross_street'], axis=1)
    return bicing


def swap(coords): # returns (lat, lon)
    return coords[::-1]

def getCoords(id, bicing):
    lon = bicing.loc[id, "lon"]
    lat = bicing.loc[id, "lat"]
    return (lon, lat)

def distance(origen, desti, bicing):
    coordA = swap(getCoords(origen, bicing))
    coordB = swap(getCoords(desti, bicing))

    return haversine(coordA, coordB, unit='m')

def walkTime(coordsA, coordsB):
    speed = 4*1000/3600
    distance = haversine(coordsA, coordsB, unit='m')
    return distance / speed

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

#POTSER CAL UNA TOLERANCIA PER A LES COMPARACIONS (???)
#CAL MIRAR QUAN HEM DE FER READ_DATAs
#FALTA DOCUMENTAR

def drawPath(path, coordsST, bicing):
    mida = 1500
    diameter = mida // 200
    thickness = mida // 300
    m = StaticMap(mida, mida, url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')
    n = len(path)

    #Plotting vertices:
    m.add_marker(CircleMarker(swap(coordsST[0]), 'yellow', diameter))
    m.add_marker(CircleMarker(swap(coordsST[1]), 'yellow', diameter))
    for id in path[1:-1]:
        coords = getCoords(id, bicing)
        marker = CircleMarker(coords, 'black', diameter)
        m.add_marker(marker)

    if n == 2:
        m.add_line(Line((swap(coordsST[0]), swap(coordsST[1])), 'blue', thickness))
    else:
        m.add_line(Line((swap(coordsST[0]), getCoords(path[1],bicing)), 'blue', thickness))
        for i in range(2, n-1):
            coordsA = getCoords(path[i-1], bicing)
            coordsB = getCoords(path[i], bicing)
            m.add_line(Line(((coordsA), (coordsB)), 'red', thickness))
        m.add_line(Line((swap(coordsST[1]), getCoords(path[-2],bicing)), 'blue', thickness))
    image = m.render()
    image.save('map.png')
    print('Done!')


def shortestPath(G, addresses):

    coordsST = addressesTOcoordinates(addresses)
    if(coordsST == None):
        return None

    G.add_nodes_from(('source', 'target'))

    #bicing = readData()
    station_ids = bicing.index.tolist()
    for id in station_ids:
        idCoords = swap(getCoords(id, bicing))
        G.add_edge('source', id, weight = walkTime(coordsST[0], idCoords))
        G.add_edge('target', id, weight = walkTime(coordsST[1], idCoords))

    weightST = walkTime(coordsST[0], coordsST[1])
    G.add_edge('source', 'target', weight=weightST)

    p = nx.dijkstra_path(G,'source','target','weight')
    drawPath(p, coordsST, bicing)

    G.remove_nodes_from(('source', 'target'))
    return p

#################################################################################
def creaGraf(max_dist):
        print('entra')
        G = nx.Graph()
        visitat = dict()
        station_ids = bicing.index.tolist()
        speed = 10*1000/3600

        for id in station_ids:
            G.add_node(id)
            visitat.update({id: False})
        for origen in station_ids:
            visitat[origen] = True;
            for desti in station_ids:
                if (not visitat[desti]):
                    dist = distance(origen, desti, bicing)
                    if (dist <= max_dist):
                        G.add_edge(origen, desti, weight = dist/speed)
        print('graf fet')
        return G



def dibuixaMapa(G):
    print('entra mapa')
    midaX = midaY = 1500
    diametre = int(midaX / 200)
    m = StaticMap(midaX, midaY, url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')

    nodes = list(G.nodes)
    for node in nodes:
        coords = getCoords(node, bicing)
        marker = CircleMarker(coords, 'black', diametre)
        m.add_marker(marker)
    print('nodes fets')

    edges = list(G.edges.data())
    gruix = int(midaX / 300)
    for edge in edges:
        origen = edge[0]
        desti  = edge[1]

        coorA = getCoords(origen, bicing)
        coorB = getCoords(desti, bicing)
        m.add_line(Line(((coorA), (coorB)), 'blue', gruix))

    print('arestes fets')

    image = m.render()
    print('render fets')

    image.save('map.png')

    print('mapa fet')

def connectedComponents(G):
    return nx.number_connected_components(G)

#Potser estaria be posar aqui dues funcions tontes que diguin edges i nodes (per cohesio)

bicing = readData()

G=creaGraf(1000)
p = shortestPath(G,'Avinguda Diagonal 92, Plaça de Sant Jaume')
p
