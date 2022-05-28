from database_scripts.param_name_list import GeoParamNameList
from database_scripts.parameter import Parameter
from database_scripts.table import Table

import os

'''Supposing main.py is run'''
LINKED_NODES_DATA_PATH = os.path.abspath('data/linked-nodes.osm.pbf')
ADDRESSES_DATA_PATH = os.path.abspath('data/addresses.osm.pbf')
DB_PATH = os.path.abspath("data/geodatabase.db")
GUI_PATH = os.path.abspath("gui/geocoder.ui")
ICON_PATH = os.path.abspath("gui/icon.png")
STREET_KINDS_PATH = os.path.abspath("data/street_kinds.txt")

GEO_TABLE_NAME = 'geo'
CITY_TABLE_NAME = 'cities'
STREETS_TABLE_NAME = 'streets'

GEO_PARAM_NAMES = GeoParamNameList('lat', 'lon', 'city', 'street',
                                   'housenumber', 'postcode')
GEO_PARAMS = [Parameter(GEO_PARAM_NAMES.lat, 'real'),
              Parameter(GEO_PARAM_NAMES.lon, 'real'),
              Parameter(GEO_PARAM_NAMES.city, 'text'),
              Parameter(GEO_PARAM_NAMES.street, 'text'),
              Parameter(GEO_PARAM_NAMES.house, 'text'),
              Parameter(GEO_PARAM_NAMES.postcode, 'int', default='null')]

GEO_TABLE = Table(GEO_TABLE_NAME, GEO_PARAMS)
CITY_TABLE = Table(CITY_TABLE_NAME, [Parameter(GEO_PARAM_NAMES.city, 'text')])
STREET_TABLE = Table(STREETS_TABLE_NAME,
                     [Parameter(GEO_PARAM_NAMES.street, 'text')])

EXTRACT_STREET_KINDS_LIMIT = 100000
