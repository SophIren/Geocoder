from parameter import Parameter
from table import Table


class ParamNameList:
    def __init__(self, lat: str, lon: str,
                 city: str, street: str, house: str, postcode: str):
        self.lat = lat
        self.lon = lon
        self.city = city
        self.street = street
        self.house = house
        self.postcode = postcode


LINKED_NODES_DATA_PATH = 'data/linked-nodes.osm.pbf'
ADDRESSES_DATA_PATH = 'data/addresses.osm.pbf'
DB_PATH = "data/geodatabase.db"

GEO_TABLE_NAME = 'geo'
CITY_TABLE_NAME = 'cities'
STREETS_TABLE_NAME = 'streets'

PARAM_NAMES = ParamNameList('lat', 'lon', 'city', 'street',
                            'housenumber', 'postcode')
PARAMS = [Parameter(PARAM_NAMES.lat, 'real'),
          Parameter(PARAM_NAMES.lon, 'real'),
          Parameter(PARAM_NAMES.city, 'text'),
          Parameter(PARAM_NAMES.street, 'text'),
          Parameter(PARAM_NAMES.house, 'text'),
          Parameter(PARAM_NAMES.postcode, 'int')]
GEO_TABLE = Table(GEO_TABLE_NAME, PARAMS)



EXTRACT_STREET_KINDS_LIMIT = 100000
