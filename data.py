import pandas as pd
import networkx as nx
import haversine as hs
import geopy as gp
import staticmap as sm

def readData():
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index='station_id')
    return bicing.drop(['physical_configuration', 'capacity', 'altitude', 'post_code', 'name', 'address'], axis=1)

def distancia(d, origen, desti):
    latA = bicing.loc[origen, "lat"]
    lonA = bicing.loc[origen, "lon"]

    latB = bicing.loc[desti, "lat"]
    lonB = bicing.loc[desti, "lon"]

    coordA = (latA, lonA)
    coordB = (latB, lonB)
    r = hs.haversine(coordA, coordB)

    if (r <= d): return True
    else: return False

#QUADRATIC: CAL MODIFICAR
def createGraph(data, dist):
    G = nx.Graph()
    visitat = dict()

    station_ids = bicing.index.tolist()
    for id in station_ids:
        G.add_node(id)
        visitat.update({id: False})
    i = 0
    for origen in station_ids:
        visitat[origen] = True;
        for desti in station_ids:
            if (visitat[desti] == False) and (distancia(dist, origen, desti) == True):
                i = i + 1
                G.add_edge(origen, desti)
    return G;

def mapGraph(G):
    midaX = 2500
    midaY = 2500
    m = sm.StaticMap(midaX, midaY, url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')

    nodes = list(G.nodes)
    for n in nodes:
        coor = (bicing.loc[n, "lon"], bicing.loc[n, "lat"])
        diametre = int(midaX / 200)
        marker = CircleMarker(coor, 'black', diametre)
        m.add_marker(marker)

    edges = list(G.edges.data())
    gruix = int(midaX / 300)
    for e in edges:
        origen = e[0]
        desti = e[1]

        latA = bicing.loc[origen, "lat"]
        lonA = bicing.loc[origen, "lon"]

        latB = bicing.loc[desti, "lat"]
        lonB = bicing.loc[desti, "lon"]

        coorA = (lonA, latA)
        coorB = (lonB, latB)
        m.add_line(Line(((coorA), (coorB)), 'blue', gruix))


    image = m.render()
    image.save('map.png')
    print('mapa fet')

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


def main():
    data = readData()
    G = createGraph(data, 1000)
    mapGraph(G)

main()
