import pandas as pd
import networkx as nx
import os
from haversine import haversine

from geopy.geocoders import Nominatim
from staticmap import *
import string
from data import dibuixaMapa


def readData():
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    stations = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index='station_id')
    stations = stations.drop(['physical_configuration', 'capacity', 'altitude', 'post_code', 'name', 'cross_street'], axis=1)
    return stations

stations = readData()
station_ids = stations.index.tolist()


# #############AUXILIARS JA HI SON A L'ORIGINIAL###################
def getCoords(id):
    lon = stations.loc[id, "lon"]
    lat = stations.loc[id, "lat"]
    return (lon, lat)


def swap(coords):  # returns (lat, lon)
    return coords[::-1]


def distance(origen, desti):
    coordA = swap(getCoords(origen))
    coordB = swap(getCoords(desti))
    return haversine(coordA, coordB, unit='m')
################################################################


def boundingBox():
    LatX, Lat_, Lon_, LonX = 0, 999, 999, 0
    for element in station_ids:
        lon, lat = getCoords(element)
        if lon < Lon_:
            Lon_ = lon
        elif lon > LonX:
            LonX = lon
        if lat > LatX:
            LatX = lat
        elif lat < Lat_:
            Lat_ = lat
    return LatX, Lat_, Lon_, LonX


def stations_matrix(dist):
    d = dist/1000
    # Diccionari de punts amb la localitzacio a la matriu
    punts = dict()
    # Convertir a graus
    d = d / 111
    LatX, Lat_, Lon_, LonX = boundingBox()
    w = int((LonX-Lon_)//d)
    h = int((LatX-Lat_)//d)

    Matrix = [[[] for x in range(w)] for y in range(h)]

    for element in station_ids:
        lon, lat = getCoords(element)
        fila = (lat - Lat_) // d
        columna = (lon - Lon_) // d
        if(fila >= h):
            fila -= 1
        if(columna >= w):
            columna -= 1
        Matrix[h-1-fila][columna].append(element)
        punts[element] = [h-1-fila, columna, 0]

    return Matrix, punts


def puntsConnexes(G, origen, punts, max_dist, directed):
    speed = 10*1000/3600
    for desti in punts:
        dist = distance(origen, desti)
        if(dist <= max_dist):
            if(not directed):
                G.add_edge(origen, desti, weight=dist/speed)
            else:
                G.add_edge(origen, desti, weight=dist)
                G.add_edge(desti, origen, weight=dist)


def grafFromMatrix(G, Matrix, points, dist, dir):
    for id in station_ids:
        G.add_node(id)
    for key in points:
        f = points[key][0]
        c = points[key][1]
        h = len(Matrix)
        w = len(Matrix[0])

        if points[key][2] != 1:
            puntsConnexes(G, key, Matrix[f][c], dist, dir)
            if f+1 < h:
                puntsConnexes(G, key, Matrix[f+1][c], dist, dir)
            if f-1 >= 0:
                puntsConnexes(G, key, Matrix[f-1][c], dist, dir)
            if c-1 >= 0:
                puntsConnexes(G, key, Matrix[f][c-1], dist, dir)
            if c+1 < w:
                puntsConnexes(G, key, Matrix[f][c+1], dist, dir)
            if f+1 < h and c-1 >= 0:
                puntsConnexes(G, key, Matrix[f+1][c-1], dist, dir)
            if f+1 < h and c+1 < w:
                puntsConnexes(G, key, Matrix[f+1][c+1], dist, dir)
            if f-1 >= 0 and c-1 >= 0:
                puntsConnexes(G, key, Matrix[f-1][c-1], dist, dir)
            if f-1 >= 0 and c+1 < w:
                puntsConnexes(G, key, Matrix[f-1][c+1], dist, dir)
            points[key][2] = 1


def grafQuadratic(G, max_dist, directed):
    visitat = dict()
    speed = 10*1000/3600
    for id in station_ids:
        G.add_node(id)
        visitat.update({id: False})
    for origen in station_ids:
        visitat[origen] = True
        for desti in station_ids:
            if (not visitat[desti]):
                dist = distance(origen, desti)
                if (dist <= max_dist):
                    if(not directed):
                        G.add_edge(origen, desti, weight=dist/speed)
                    else:
                        G.add_edge(origen, desti, weight=dist)
                        G.add_edge(desti, origen, weight=dist)


def grafLinial(G, max_dist, directed):
    if max_dist >= 5:
        Matrix, points = stations_matrix(max_dist)
        grafFromMatrix(G, Matrix, points, max_dist, directed)


def creaGraf(max_dist, directed):
    if(not directed):
        G = nx.Graph()
    else:
        G = nx.DiGraph()

    if max_dist >= 50:
        grafLinial(G, max_dist, directed)
    else:
        grafQuadratic(G, max_dist, directed)

    return G


def main():
    d = 600

    G = creaGraf(d, False)
    print(G.number_of_edges())
    dibuixaMapa(G, "linial.jpg")
