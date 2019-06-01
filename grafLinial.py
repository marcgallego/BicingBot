import pandas as pd
import networkx as nx
import os

from pandas import DataFrame, Series
from haversine import haversine

from geopy.geocoders import Nominatim
from staticmap import *
import string


def readData():
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    stations = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index='station_id')
    stations = stations.drop(['physical_configuration', 'capacity', 'altitude', 'post_code', 'name', 'cross_street'], axis=1)
    return stations

stations = readData()
station_ids = stations.index.tolist()

def getCoords(id):
    lon = stations.loc[id, "lon"]
    lat = stations.loc[id, "lat"]
    return (lon, lat)

def boundingBox():
    LatE, LatD, LonS, LonI = 9999, 0, 0, 9999
    for element in station_ids:
        lon, lat = getCoords(element)
        if lon > LonS:
            LonS = lon
        elif lon < LonI:
            LonI = lon
        if lat < LatE:
            LatE = lat
        elif lat > LatD:
            LatD = lat
    return LatE, LatD, LonS, LonI

# d es la distancia
def coordenades(d):
    #Convertir de km a graus(1grau = 111km)
    d = d / 111

    LatE, LatD, LonS, LonI = boundingBox()
    coordenadesLatitud = []
    coordenadesLatitud.append(LatE)

    coordenadesLongitud = []
    coordenadesLongitud.append(LonI)

    iterador = LatE
    while iterador <= LatD:
        iterador = iterador + d
        coordenadesLatitud.append(iterador)
    coordenadesLatitud.append(iterador)

    iterador = LonI
    while iterador <= LonS:
        iterador = iterador + d
        coordenadesLongitud.append(iterador)
    coordenadesLongitud.append(iterador)

    bbox = [LatE, LatD, LonS, LonI]
    return coordenadesLatitud, coordenadesLongitud, bbox


def matriu(coordenadesLatitud, coordenadesLongitud):
    amplada, alçada = len(coordenadesLatitud)-1, len(coordenadesLongitud)-1;
    Matrix = [[[] for x in range(amplada)] for y in range(alçada)]
    coordenadesLongitud = coordenadesLongitud.reverse()
    for element in station_ids:
        lon, lat = getCoords(element)



        j = 0
        while(lat > coordenadesLatitud[j]):
            j += 1

        i = 0
        '''
        while(lon < coordenadesLongitud[i]):
            i += 1
        '''
#[h][w]
        Matrix[i][j-1].append(element)


    return Matrix


def dibuixaMapa(coordenadesLatitud, coordenadesLongitud, bbox):
    #    bbox = [LatE, LatD, LonS, LonI]
    LatE = bbox[0]
    LatD = bbox[1]
    LonS = bbox[2]
    LonI = bbox[3]
    photoName = 'quad.png'

    midaX = midaY = 1500
    diametre = midaX // 180
    gruix = midaX // 300

    m = StaticMap(midaX, midaY)

    for coor in coordenadesLongitud:
        coorA = (coor, LatE)
        coorB = (coor, LatD)
        m.add_line(Line(((coorA), (coorB)), 'blue', gruix))

    for coor in coordenadesLatitud:
        coorA = (LonS, coor)
        coorB = (LonI, coor)
        m.add_line(Line(((coorA), (coorB)), 'blue', gruix))

    #nodes
    m.add_marker(CircleMarker((LonS, LatD), 'black', diametre))
    m.add_marker(CircleMarker((LonI, LatD), 'black', diametre))
    m.add_marker(CircleMarker((LonS, LatE), 'black', diametre))
    m.add_marker(CircleMarker((LonI, LatE), 'black', diametre))

    image = m.render()
    image.save(photoName)

def main():
    d = 2
    coordenadesLatitud, coordenadesLongitud, bbox = coordenades(d)
    print('Calculs fets')
    dibuixaMapa(coordenadesLatitud, coordenadesLongitud, bbox)
    print(matriu(coordenadesLatitud, coordenadesLongitud))
    print(coordenadesLatitud, coordenadesLongitud)
    print(bbox)
main()
