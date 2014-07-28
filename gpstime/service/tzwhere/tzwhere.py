
from msgpack import loads
import datetime
import math
import os
import pickle


class tzwhere(object):
    SHORTCUT_DEGREES_LATITUDE = 1
    SHORTCUT_DEGREES_LONGITUDE = 1
    DEFAULT_FILENAME = os.path.join(os.path.dirname(__file__),
        'tzdata.msgpack')

    def __init__(self, filename=DEFAULT_FILENAME, read_pickle=False,
            write_pickle=False):

        input_file = open(filename, 'r')
        featureCollection = loads(input_file.read())

        input_file.close()

        if write_pickle:
            f = open(PICKLE_FILENAME, 'w')
            pickle.dump(featureCollection, f, pickle.HIGHEST_PROTOCOL)
            f.close()


        self.timezoneNamesToPolygons = {}
        for feature in featureCollection['features']:

            tzname = feature['properties']['TZID']
            if feature['geometry']['type'] == 'Polygon':
                polys = feature['geometry']['coordinates']
                if polys and not (tzname in self.timezoneNamesToPolygons):
                    self.timezoneNamesToPolygons[tzname] = []

                for raw_poly in polys:
                    #WPS84 coordinates are [long, lat], while many conventions are [lat, long]
                    #Our data is in WPS84.  Convert to an explicit format which geolib likes.
                    assert len(raw_poly)%2 == 0
                    poly = []
                    while raw_poly:
                        lat = raw_poly.pop()
                        lng = raw_poly.pop()
                        poly.append({'lat': lat, 'lng': lng})
                    self.timezoneNamesToPolygons[tzname].append(tuple(poly))

        self.timezoneLongitudeShortcuts = {};
        self.timezoneLatitudeShortcuts = {};
        for tzname in self.timezoneNamesToPolygons:
            for polyIndex, poly in enumerate(self.timezoneNamesToPolygons[tzname]):
                lats = [x['lat'] for x in poly]
                lngs = [x['lng'] for x in poly]
                minLng = math.floor(min(lngs) / self.SHORTCUT_DEGREES_LONGITUDE) * self.SHORTCUT_DEGREES_LONGITUDE;
                maxLng = math.floor(max(lngs) / self.SHORTCUT_DEGREES_LONGITUDE) * self.SHORTCUT_DEGREES_LONGITUDE;
                minLat = math.floor(min(lats) / self.SHORTCUT_DEGREES_LATITUDE) * self.SHORTCUT_DEGREES_LATITUDE;
                maxLat = math.floor(max(lats) / self.SHORTCUT_DEGREES_LATITUDE) * self.SHORTCUT_DEGREES_LATITUDE;
                degree = minLng
                while degree <= maxLng:
                    if degree not in self.timezoneLongitudeShortcuts:
                        self.timezoneLongitudeShortcuts[degree] = {}

                    if tzname not in self.timezoneLongitudeShortcuts[degree]:
                        self.timezoneLongitudeShortcuts[degree][tzname] = []

                    self.timezoneLongitudeShortcuts[degree][tzname].append(polyIndex)
                    degree = degree + self.SHORTCUT_DEGREES_LONGITUDE

                degree = minLat
                while degree <= maxLat:
                    if degree not in self.timezoneLatitudeShortcuts:
                        self.timezoneLatitudeShortcuts[degree] = {}

                    if tzname not in self.timezoneLatitudeShortcuts[degree]:
                        self.timezoneLatitudeShortcuts[degree][tzname] = []

                    self.timezoneLatitudeShortcuts[degree][tzname].append(polyIndex)
                    degree = degree + self.SHORTCUT_DEGREES_LATITUDE

        #convert things to tuples to save memory
        for tzname in self.timezoneNamesToPolygons.keys():
            self.timezoneNamesToPolygons[tzname] = tuple(self.timezoneNamesToPolygons[tzname])
        for degree in self.timezoneLatitudeShortcuts:
            for tzname in self.timezoneLatitudeShortcuts[degree].keys():
                self.timezoneLatitudeShortcuts[degree][tzname] = tuple(self.timezoneLatitudeShortcuts[degree][tzname])
        for degree in self.timezoneLongitudeShortcuts.keys():
            for tzname in self.timezoneLongitudeShortcuts[degree].keys():
                self.timezoneLongitudeShortcuts[degree][tzname] = tuple(self.timezoneLongitudeShortcuts[degree][tzname])

    def _point_inside_polygon(self, x, y, poly):
        n = len(poly)
        inside =False

        p1x, p1y = poly[0]['lng'], poly[0]['lat']
        for i in range(n+1):
            p2x,p2y = poly[i % n]['lng'], poly[i % n]['lat']
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x,p1y = p2x,p2y

        return inside

    def tzNameAt(self, latitude, longitude):
        latTzOptions = self.timezoneLatitudeShortcuts[math.floor(latitude / self.SHORTCUT_DEGREES_LATITUDE) * self.SHORTCUT_DEGREES_LATITUDE]
        latSet = set(latTzOptions.keys());
        lngTzOptions = self.timezoneLongitudeShortcuts[math.floor(longitude / self.SHORTCUT_DEGREES_LONGITUDE) * self.SHORTCUT_DEGREES_LONGITUDE]
        lngSet = set(lngTzOptions.keys())
        possibleTimezones = lngSet.intersection(latSet);
        if possibleTimezones:
            if False and len(possibleTimezones) == 1:
                return possibleTimezones.pop()
            else:
                for tzname in possibleTimezones:
                    polyIndices = set(latTzOptions[tzname]).intersection(set(lngTzOptions[tzname]));
                    for polyIndex in polyIndices:
                        poly = self.timezoneNamesToPolygons[tzname][polyIndex];
                        if self._point_inside_polygon(longitude, latitude, poly):
                            return tzname

