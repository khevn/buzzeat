import requests
import geopy
from geopy.distance import vincenty


def google_api(location):
    # look up location using Google maps API

    locInfo = requests.get(
        'https://maps.googleapis.com/maps/api/geocode/json?address='
        + location + '&sensor=false').json()

    geoInfo = {}
    if locInfo['status'] != 'ZERO_RESULTS':
        geoInfo = {'formatted_address': locInfo['results'][0]['formatted_address'],
                'lat': locInfo['results'][0]['geometry']['location']['lat'],
                'lng': locInfo['results'][0]['geometry']['location']['lng']}
    else:
        print 'no match' + location

    return geoInfo


def loc_bounds(origin, distance):
    # returns the four edge coordinates of the bounding square box
    # specified by the distance around the origin

    north_c = vincenty(kilometers=distance).destination(geopy.Point(origin), 0)
    east_c = vincenty(kilometers=distance).destination(geopy.Point(origin), 90)
    south_c = vincenty(kilometers=distance).destination(geopy.Point(origin), 180)
    west_c = vincenty(kilometers=distance).destination(geopy.Point(origin), 270)

    geo_box = (south_c.latitude, north_c.latitude, west_c.longitude, east_c.longitude)

    return geo_box