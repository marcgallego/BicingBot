import pandas as pd
import networkx as nx
import os

from pandas import DataFrame, Series
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

##############AUXILIARS JA HI SON A L'ORIGINIAL###################
def getCoords(id):
    lon = stations.loc[id, "lon"]
    lat = stations.loc[id, "lat"]
    return (lon, lat)

def swap(coords): # returns (lat, lon)
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

def matriu(dist):
    d = dist/1000
    #Diccionari de punts amb la localitzacio a la matriu
    punts = dict()
    #Convertir a graus
    d = d / 111
    LatX, Lat_, Lon_, LonX = boundingBox()
    w = int((LonX-Lon_)//d)
    h = int((LatX-Lat_)//d)

    Matrix = [[[] for x in range(w)] for y in range(h)]

    for element in station_ids:
        lon, lat = getCoords(element)
        fila = int((lat - Lat_)//d)
        columna = int((lon - Lon_)//d)
        if(fila >= h):
            fila -= 1
        if(columna >= w):
            columna -= 1
        Matrix[h-1-fila][columna].append(element)
        punts[element] = [h-1-fila, columna, 0]

    return Matrix, punts


def puntsConnexes(G, origen, punts, d):
    speed = 10*1000/3600
    for desti in punts:
        dist = distance(origen,desti)
        if(dist <= d):
            G.add_edge(origen, desti, weight = dist/speed)


def grafFromMatrix(Matrix, punts, d):
    G = nx.Graph()
    for id in station_ids:
        G.add_node(id)
    for key in punts:
        f = punts[key][0]
        c = punts[key][1]
        h = len(Matrix)
        w = len(Matrix[0])

        if punts[key][2] != 1:
            puntsConnexes(G, key, Matrix[f][c], d)
            if f+1 < h:
                puntsConnexes(G, key, Matrix[f+1][c], d)
            if f-1 >= 0:
                puntsConnexes(G, key, Matrix[f-1][c], d)
            if c-1 >= 0:
                puntsConnexes(G, key, Matrix[f][c-1], d)
            if c+1 < w:
                puntsConnexes(G, key, Matrix[f][c+1], d)
            if f+1 < h and c-1 >= 0:
                puntsConnexes(G, key, Matrix[f+1][c-1], d)
            if f+1 < h and c+1 < w:
                puntsConnexes(G, key, Matrix[f+1][c+1], d)
            if f-1 >= 0 and c-1 >= 0:
                puntsConnexes(G, key, Matrix[f-1][c-1], d)
            if f-1 >= 0 and c+1 < w:
                puntsConnexes(G, key, Matrix[f-1][c+1], d)
            punts[key][2] = 1
    return G

def grafQuadratic(max_dist):
    G = nx.Graph()
    visitat = dict()
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
    return G

def grafLinial(d):
    if d >= 5:
        Matrix, punts = matriu(d)
        return grafFromMatrix(Matrix, punts, d)
    else:
        return 0

def creaGraf(max_dist):
    G = nx.Graph()
    if max_dist >= 50:
        G = grafLinial(max_dist)
    else:
        G = grafQuadratic(max_dist)
    return G

def main():
    d = 600

    G = grafLinial(d)
    print(G.number_of_edges())
    dibuixaMapa(G, "linial.jpg")

    Q = grafQuadratic(d)
    print(Q.number_of_edges())
    dibuixaMapa(Q, "quadratic.jpg")

main()
