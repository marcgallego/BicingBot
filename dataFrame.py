import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from pandas import DataFrame
from haversine import haversine
from geopy.geocoders import Nominatim

####DADES####
distancia_vertex = 0.5
grafic = "circular"     #"standar", "random", "circular", "spring"
############

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

def drawGraph(G):
    options = {
        'node_color': 'black',
        'node_size': 5,
        'line_color': 'grey',
        'linewidths': 0,
        'width': 0.5,
    }
    if grafic == "standard":
        nx.draw(G, with_labels=False, **options)
        plt.savefig("graf.png")

    if grafic == "random":
        nx.draw_random(G, with_labels=False, **options)
        plt.savedistancia_vertexfig("rand.png")

    if grafic == "circular":
        nx.draw_circular(G, with_labels=False, **options)
        plt.savefig("circ.png")

    if grafic == "spring":
        nx.draw_spring(G, with_labels=False, **options)
        plt.savefig("spring.png")

def creaGraf(G):
        d = distancia_vertex
        visitat = dict()

        for id in station_ids:
            G.add_node(id)
            visitat.update({id: False})
        i = 0
        for origen in station_ids:
            visitat[origen] = True;
            for desti in station_ids:
                if (visitat[desti] == False) and (distancia(d, origen, desti) == True):
                    i = i + 1
                    G.add_edge(origen, desti)
        return i;

def main():
    G = nx.Graph()
    ed = creaGraf(G)
    drawGraph(G)
    print('Graf fet')
    print('Vertexs: ', len(station_ids), 'Edges: ', ed)

main()
