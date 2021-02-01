
import gmplot
import googlemaps
from datetime import datetime
import csv
import pandas as pd
import numpy as np

# TODO: move API-key to a file
# TODO: make a class that maintains the state (e.g. API-key)
#   - initialise with the API key
# TODO: make a git repository
# TODO: read rides directly from an activity app

routefilename = 'data/Directions_from_Battery_Bikeway_New_York_NY_USA_to_' \
                'Lost_World_Caverns_Lost_World_Road_Lewisburg_WV_USA.csv'
bikingfile = 'data/biking.csv'


class Route:
    def __init__(self,apifile='googleapikey.txt'):
        self.apifile = apifile
        try:
            with open(apifile) as f:
                self.apikey = f.readline().strip()
        except Exception as e:
            print(e, 'exiting')
            exit(-1)


def read_route(Route, filename):
    addresses = []
    with open(filename) as f:
        data = csv.reader(f)
        for row in data:
            if 'Directions from' not in row[2] and 'Name' not in row[2]:
                addresses += [row[2]]
    Route.waypoints = addresses


def read_biking(Route, bikingfile):
    bikings = pd.read_csv(bikingfile)
    bikings['cumulative'] = np.cumsum(bikings.length)
    Route.bikings = bikings


def get_center(route):
    return np.mean([route['bounds']['northeast']['lat'], route['bounds']['southwest']['lat']]), \
           np.mean([route['bounds']['northeast']['lng'], route['bounds']['southwest']['lng']])


def drop_after_draw_until(bikings, draw_until):
    inds = np.array([datetime.strptime(x, '%Y-%m-%d').date() for x in bikings['day']]) < \
           datetime.strptime(draw_until, '%Y-%m-%d').date()
    return bikings[inds].copy()


def draw_route(Route, draw_until='', verbose=0):
    legs = []
    steps = []
    distance = [0]
    if draw_until != '':
        Route.bikings = drop_after_draw_until(Route.bikings, draw_until)
    sofar = np.sum(Route.bikings.length)
    for leg in Route.route['legs']:
        legs.append([leg['start_location']['lat'], leg['start_location']['lng']])
        if verbose: print(leg['distance']['text'], leg['start_location'])
        for step in leg['steps']:
            if verbose: print('\t', step['distance']['text'], step['end_location'])
            steps.append([step['end_location']['lat'], step['end_location']['lng']])
            distance += [distance[-1] + step['distance']['value'] / 1000]
    distance = np.array(distance[1:])
    steps = pd.DataFrame.from_records(steps, columns=['latitude', 'longitude'])
    steps['done'] = distance < sofar
    legs.append([leg['end_location']['lat'], leg['end_location']['lng']])
    legs = pd.DataFrame.from_records(legs, columns=['latitude', 'longitude'])
    Route.bikings['latitude'] = 0.
    Route.bikings['longitude'] = 0.
    for ind, biking in Route.bikings.iterrows():
        Route.bikings.at[ind, 'latitude'] = steps.iloc[np.argmax(distance > biking.cumulative) - 1]['latitude']
        Route.bikings.at[ind, 'longitude'] = steps.iloc[np.argmax(distance > biking.cumulative) - 1]['longitude']
    lat, lng = get_center(Route.route)
    gmapfig = gmplot.GoogleMapPlotter(lat, lng, 7)
    gmapfig.plot(steps.latitude, steps.longitude, 'cornflowerblue', edge_width=5)
    sofar = steps[steps['done']]
    gmapfig.plot(sofar.latitude, sofar.longitude, 'red', edge_width=5)
    # TODO: text not yet visible, but markers are showing
    for latitude, longitude, text in zip(Route.bikings.latitude, Route.bikings.longitude, Route.bikings.day):
        gmapfig.marker(latitude, longitude, title=text, size=40)
    gmapfig.apikey = Route.apikey
    gmapfig.draw("map.html")
    print(f"footer: #virtualroadtrip #bikeday{len(Route.bikings)} {Route.bikings.iloc[-1, 0]} {np.int(sum(Route.bikings['length']))} km")


if __name__ == '__main__':
    Route = Route()
    read_route(Route, routefilename)
    read_biking(Route, bikingfile)
    gmaps = googlemaps.Client(key=Route.apikey)

    # Request directions via bicycling
    now = datetime.now()
    Route.route = gmaps.directions(Route.waypoints[0],
                                         Route.waypoints[-1],
                                         waypoints=Route.waypoints[1:-1],
                                         mode="bicycling",
                                         units="metric",
                                         departure_time=now)[0]

    draw_route(Route, draw_until='')