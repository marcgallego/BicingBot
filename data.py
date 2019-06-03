import os
import pandas as pd
import networkx as nx
import itertools as it
from haversine import haversine

from geopy.geocoders import Nominatim
from staticmap import *
import string

def getBikes():
    url_status = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status'
    bikes = DataFrame.from_records(pd.read_json(url_status)['data']['stations'], index='station_id')
    bikes = bikes[['num_bikes_available', 'num_docks_available']]
    return bikes

def getStations():
    url_info = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    stations = pd.DataFrame.from_records(pd.read_json(url_info)['data']['stations'], index='station_id')
    stations = stations[['address', 'lat', 'lon']]
    return stations

stations = getStations()


def swap(coords): # returns (lat, lon)
    return coords[::-1]


def getCoords(id, stations):
    lon = stations.loc[id, "lon"]
    lat = stations.loc[id, "lat"]
    return (lon, lat)


def distance(origen, desti):
    coordA = swap(getCoords(origen, stations))
    coordB = swap(getCoords(desti, stations))
    return haversine(coordA, coordB, unit='m')


def walkTime(coordsA, coordsB):
    speed = 4*1000/3600
    distance = haversine(coordsA, coordsB, unit='m')
    return distance / speed


def addressesTOcoordinates(addresses):
    try:
        geolocator = Nominatim(user_agent="stations_bot")
        address1, address2 = addresses.split(',')
        location1 = geolocator.geocode(address1 + ', Barcelona')
        location2 = geolocator.geocode(address2 + ', Barcelona')
        return (location1.latitude, location1.longitude), (location2.latitude, location2.longitude)
    except:
        return None


def drawPath(path, coordsST, photoName):
    mida = 1500
    diameter = mida // 180
    thickness = mida // 300
    m = StaticMap(mida, mida)
    n = len(path)

    #Plotting vertices:
    m.add_marker(CircleMarker(swap(coordsST[0]), 'black', diameter*2))
    m.add_marker(CircleMarker(swap(coordsST[0]), 'white', diameter))

    m.add_marker(CircleMarker(swap(coordsST[1]), 'black', diameter*2))
    m.add_marker(CircleMarker(swap(coordsST[1]), 'white', diameter))

    for id in path[1:-1]:
        coords = getCoords(id, stations)
        marker = CircleMarker(coords, 'black', diameter)
        m.add_marker(marker)

    if n == 2:
        m.add_line(Line((swap(coordsST[0]), swap(coordsST[1])), 'red', thickness))
    else:
        m.add_line(Line((swap(coordsST[0]), getCoords(path[1],stations)), 'red', thickness))
        for i in range(2, n-1):
            coordsA = getCoords(path[i-1], stations)
            coordsB = getCoords(path[i], stations)
            m.add_line(Line(((coordsA), (coordsB)), 'blue', thickness))
        m.add_line(Line((swap(coordsST[1]), getCoords(path[-2],stations)), 'red', thickness))
    image = m.render()
    image.save(photoName)
    print('Done!')


def shortestPath(G, addresses, photoName):
    print("entra shortest path")

    coordsST = addressesTOcoordinates(addresses)
    if(coordsST == None):
        return None
    G.add_nodes_from(('source', 'target'))

    #stations = getStations()
    station_ids = stations.index.tolist()
    for id in station_ids:
        idCoords = swap(getCoords(id, stations))
        G.add_edge('source', id, weight = walkTime(coordsST[0], idCoords))
        G.add_edge('target', id, weight = walkTime(coordsST[1], idCoords))

    weightST = walkTime(coordsST[0], coordsST[1])
    G.add_edge('source', 'target', weight=weightST)

    p = nx.dijkstra_path(G,'source','target','weight')
    drawPath(p, coordsST, photoName)

    G.remove_nodes_from(('source', 'target'))
    return p


def creaGraf(max_dist):
    print('entra')
    G = nx.Graph()
    visitat = dict()
    station_ids = stations.index.tolist()
    speed = 10*1000/3600

    for id in station_ids:
        G.add_node(id)
        visitat.update({id: False})
    for origen in station_ids:
        visitat[origen] = True;
        for desti in station_ids:
            if (not visitat[desti]):
                dist = distance(origen, desti)
                if (dist <= max_dist):
                    G.add_edge(origen, desti, weight = dist/speed)
    print('graf fet')
    return G


def dibuixaMapa(G, photoName):
    print('entra mapa')
    midaX = midaY = 1500
    diametre = midaX // 180
    m = StaticMap(midaX, midaY)

    nodes = list(G.nodes)
    for node in nodes:
        coords = getCoords(node, stations)
        m.add_marker(CircleMarker(coords, 'black', diametre*2))
        m.add_marker(CircleMarker(coords, 'white', diametre))
    print('nodes fets')

    edges = list(G.edges.data())
    gruix = midaX // 300
    for edge in edges:
        origen = edge[0]
        desti  = edge[1]

        coorA = getCoords(origen, stations)
        coorB = getCoords(desti, stations)
        m.add_line(Line(((coorA), (coorB)), 'blue', gruix))

    print('arestes fets')

    image = m.render()
    print('render fets')

    image.save(photoName)

    print('mapa fet')

def distributeBikes(radius, requiredBikes, requiredDocks):
    DG = nx.DiGraph()
    DG.add_node('TOP') # The green node
    demand = 0

    bikes = getBikes()
    for st in bikes.itertuples():
        idx = st.Index # Station ID
        if idx not in stations.index: continue
        stridx = str(idx)

        # The blue (s), black (g) and red (t) nodes of the graph
        s_idx, g_idx, t_idx = 's'+stridx, 'g'+stridx, 't'+stridx
        DG.add_node(g_idx)
        DG.add_node(s_idx)
        DG.add_node(t_idx)

        b, d = st.num_bikes_available, st.num_docks_available
        req_bikes = max(0, requiredBikes - b)
        req_docks = max(0, requiredDocks - d)

        # Some of the following edges require attributes (posar capacitats)
        DG.add_edge('TOP', s_idx)
        DG.add_edge(t_idx, 'TOP')
        DG.add_edge(s_idx, g_idx, capacity = max(0, b - requiredBikes)) #Bicis que puc rebre per seguir tenint n docks
        DG.add_edge(g_idx, t_idx, capacity = max(0, d - requiredDocks)) #Bicis que puc donar per seguir tenint m bicis

        if req_bikes > 0:
            demand += req_bikes
            DG.nodes[t_idx]['demand'] = req_bikes
        elif req_docks > 0:
            demand -= req_docks
            DG.nodes[s_idx]['demand'] = -req_docks

    DG.nodes['TOP']['demand'] = -demand # The sum of the demands must be zero



#Potser estaria be posar aqui dues funcions tontes que diguin edges i nodes (per cohesio)
def connectedComponents(G):
    return nx.number_connected_components(G)

def nodesGraph(G):
    return G.number_of_nodes()

def edgesGraph(G):
    return G.number_of_edges()


distributeBikes(1,2,3)
