import sys

from request_parsing import GeoParser
from database_scripts.DB import DataBase

import settings

sys.stdout = GeoParser(DataBase([settings.GEO_TABLE, settings.CITY_TABLE,
                                 settings.STREET_TABLE])).parse(sys.argv[1])
