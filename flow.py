import pandas as pd
import networkx as nx
#import itertools as it
from haversine import haversine
from pandas import DataFrame

from data import getBikes, getStations
from graf import creaGraf

stations = getStations()
bikes = getBikes()

radius = 1000     # Radius for the geometric graph (you will have to use your current geometric graph)
requiredBikes = 2 # Required number of bikes (this will be a parameter of your command)
requiredDocks = 0 # Required number of docks (this will be a parameter of your command)

nbikes = 'num_bikes_available'
ndocks = 'num_docks_available'

print(len(bikes.loc[(bikes[nbikes] < requiredBikes) | (bikes[ndocks] < requiredDocks)]))


G = creaGraf(radius, True)
G.add_node('TOP') # The green node
demand = 0

### Iterem per totes les estacions:
for st in bikes.itertuples():
    idx = st.Index # Station ID
    if idx not in stations.index: continue
    stridx = str(idx)

    # The blue (s), black (g) and red (t) nodes of the graph
    s_idx, g_idx, t_idx = 's'+stridx, idx, 't'+stridx
    #G.add_node(g_idx)
    G.add_node(s_idx)
    G.add_node(t_idx)

    b, d = st.num_bikes_available, st.num_docks_available
    req_bikes = max(0, requiredBikes - b)
    req_docks = max(0, requiredDocks - d)

    # Some of the following edges require attributes (posar capacitats)
    G.add_edge('TOP', s_idx)
    G.add_edge(t_idx, 'TOP')
    G.add_edge(s_idx, g_idx, capacity = max(0, b - requiredBikes)) #Bicis que puc rebre per seguir tenint n docks
    G.add_edge(g_idx, t_idx, capacity = max(0, d - requiredDocks)) #Bicis que puc donar per seguir tenint m bicis

    if req_bikes > 0:
        demand += req_bikes
        G.nodes[t_idx]['demand'] = req_bikes
    elif req_docks > 0:
        demand -= req_docks
        G.nodes[s_idx]['demand'] = -req_docks


G.nodes['TOP']['demand'] = -demand # The sum of the demands must be zero



print('Graph with', G.number_of_nodes(), "nodes and", G.number_of_edges(), "edges.")

err = False

try:
    flowCost, flowDict = nx.network_simplex(G)

except nx.NetworkXUnfeasible:
    err = True
    print("No solution could be found")

except:
    err = True
    print("Something bad happened!")



if not err:

    print("The total cost of transferring bikes is", flowCost/1000, "km.")

    # We update the status of the stations according to the calculated transportation of bicycles
    for src in flowDict:

        if isinstance(src, int) or src == 'TOP': continue
        idx_src = int(src[1:])
        for dst, b in flowDict[src].items():
            if isinstance(src, int) and b > 0:
                idx_dst = int(dst)
                print(idx_src, "->", idx_dst, " ", b, "bikes, distance", G.edges[src, dst]['weight'])
                bikes.at[idx_src, nbikes] -= b
                bikes.at[idx_dst, nbikes] += b
                bikes.at[idx_src, ndocks] += b
                bikes.at[idx_dst, ndocks] -= b


print(len(bikes.loc[(bikes[nbikes] < requiredBikes) | (bikes[ndocks] < requiredDocks)]))
