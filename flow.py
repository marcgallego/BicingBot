import pandas as pd
import networkx as nx
import itertools as it
from haversine import haversine
from pandas import DataFrame


url_info = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
url_status = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status'
stations = DataFrame.from_records(pd.read_json(url_info)['data']['stations'], index='station_id')
bikes = DataFrame.from_records(pd.read_json(url_status)['data']['stations'], index='station_id')


nbikes = 'num_bikes_available'
ndocks = 'num_docks_available'
bikes = bikes[[nbikes, ndocks]] # We only select the interesting columns

TotalBikes = bikes[nbikes].sum()
TotalDocks = bikes[ndocks].sum()
print("Total number of bikes:", TotalBikes)
print("Total number of docks:", TotalDocks)


radius = 1000     # Radius for the geometric graph (you will have to use your current geometric graph)
requiredBikes = 1 # Required number of bikes (this will be a parameter of your command)
requiredDocks = 2 # Required number of docks (this will be a parameter of your command)

print(len(bikes.loc[(bikes[nbikes] < requiredBikes) | (bikes[ndocks] < requiredDocks)]))


G = nx.DiGraph()
G.add_node('TOP') # The green node
demand = 0

### Iterem per totes les estacions:
for st in bikes.itertuples():
    idx = st.Index # Station ID
    if idx not in stations.index: continue
    stridx = str(idx)

    # The blue (s), black (g) and red (t) nodes of the graph
    s_idx, g_idx, t_idx = 's'+stridx, 'g'+stridx, 't'+stridx
    G.add_node(g_idx)
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

for idx1, idx2 in it.combinations(stations.index.values, 2):
    coord1 = (stations.at[idx1, 'lat'], stations.at[idx1, 'lon'])
    coord2 = (stations.at[idx2, 'lat'], stations.at[idx2, 'lon'])
    dist = haversine(coord1, coord2, unit='m')
    if dist <= radius:
        dist = int(dist)
        # The edges must be bidirectional: g_idx1 <--> g_idx2
        G.add_edge('g'+str(idx1), 'g'+str(idx2), weight=dist)
        G.add_edge('g'+str(idx2), 'g'+str(idx1), weight=dist)

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
        if src[0] != 'g': continue
        idx_src = int(src[1:])
        for dst, b in flowDict[src].items():
            if dst[0] == 'g' and b > 0:
                idx_dst = int(dst[1:])
                print(idx_src, "->", idx_dst, " ", b, "bikes, distance", G.edges[src, dst]['weight'])
                bikes.at[idx_src, nbikes] -= b
                bikes.at[idx_dst, nbikes] += b
                bikes.at[idx_src, ndocks] += b
                bikes.at[idx_dst, ndocks] -= b


TotalBikes = bikes[nbikes].sum()
TotalDocks = bikes[ndocks].sum()
print("Total number of bikes:", TotalBikes)
print("Total number of docks:", TotalDocks)


print(len(bikes.loc[(bikes[nbikes] < requiredBikes) | (bikes[ndocks] < requiredDocks)]))
