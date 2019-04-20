import requests
import xml
from xml.etree import ElementTree
import pandas as pd
import time
import datetime

def get_predictions(stop_id, a='ttc'):
    url = 'http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a={a}&stopId={StopID}'.format(
        StopID=stop_id, a=a)
    r = requests.get(url)
    root = ElementTree.fromstring(r.content)
    trips = []
    for route in root.iter('predictions'):
        for direction in route.iter('direction'):
            for prediction in direction.iter('prediction'):
                trip = pd.Series(prediction.attrib)
                trip['direction'] = direction.attrib['title']
                trip['time'] = datetime.datetime.fromtimestamp(float(trip['epochTime'])/1000.)

                # Append route info
                for field in route.attrib.keys():
                    trip[field] = route.attrib[field]

                # Append bus whereabouts
                bus = get_vehicle_location(r=trip['routeTag'], v=trip['vehicle'], return_attrib=True)
                for field in bus.keys():
                    trip[field] = bus[field]

                trips.append(pd.DataFrame(trip).T)

    trips = pd.concat(trips, sort=True)
    return trips
    
def get_schedule(r, a='ttc'):
    return None
    
def get_vehicle_location(r, v, a='ttc', return_attrib=False):
    url = 'http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocation&a=ttc&r={r}&v={v}'.format(
        r=r, v=v, a='ttc')
    r = requests.get(url)
    root = ElementTree.fromstring(r.content)

    buses = []
    for bus in root.iter('vehicle'):
        if return_attrib:
            return bus.attrib
        bus = pd.DataFrame(pd.Series(bus.attrib)).T
        buses.append(bus)
    buses = pd.concat(buses)
    return buses
    #return buses[0]
    
def get_messages(r, a='ttc'):
    return None

if __name__ == '__main__':
    poll_frequency = 60
    last_minute = -1
    while(True):
        this_minute = datetime.datetime.now().minute
        if this_minute != last_minute:
            last_minute = this_minute
            # If we should update
            predictions = get_predictions(1349)
            display = predictions[['branch','minutes','seconds','predictable','secsSinceReport','vehicle','affectedByLayover']].fillna(False)
            coords = predictions[['lat','lon']]
            print(display)