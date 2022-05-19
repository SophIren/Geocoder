class GeoParamNameList:
    def __init__(self, lat: str = None, lon: str = None,
                 city: str = None, street: str = None, house: str = None,
                 postcode: str = None):
        self.lat = lat
        self.lon = lon
        self.city = city
        self.street = street
        self.house = house
        self.postcode = postcode
