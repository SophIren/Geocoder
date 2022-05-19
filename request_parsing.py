import re
from typing import Set
from database_scripts import DB
import settings


class GeoParser:
    def __init__(self, db: DB.DataBase):
        self.db = db
        self.street_kinds = self.extract_street_kinds()

    def extract_street_kinds(self) -> Set[str]:
        streets = self.db.get_entries_by_column(
            settings.STREET_TABLE,
            settings.GEO_PARAM_NAMES.street,
            settings.EXTRACT_STREET_KINDS_LIMIT
        )
        street_kinds = set()

        for street in streets:
            for word in re.split("[/. ]", street[0]):
                if word and word[0].islower(): # This is bad
                    street_kinds.add(word)

        return street_kinds

    def parse(self, line: str):
        tokens = re.split("[;,. ]", line)

        city = None
        street = None
        house = None
        for token in tokens:
            if token in self.street_kinds:
                continue
            if city is None:
                city = self.db.filter_by_values(settings.CITY_TABLE, {
                    settings.GEO_PARAM_NAMES.city: token})[0][1]
                if city:
                    continue
            if street is None:
                street = self.db.filter_by_values(settings.STREET_TABLE, {
                    settings.GEO_PARAM_NAMES.street: token})
                # Remove the index from here (i. e. change the filter method)
                if street:
                    street = street[0][1]
                    continue
            if token[0].isdigit():  # Regex needed
                house = token

        if city is None or street is None or house is None:
            pass  # Wrong

        values = {
            settings.GEO_PARAM_NAMES.city: city,
            settings.GEO_PARAM_NAMES.street: street,
            settings.GEO_PARAM_NAMES.house: house
        }
        return list(self.db.filter_by_values(settings.GEO_TABLE, values))
        # sort by street kind (if specified) and housenumber


if __name__ == "__main__":
    db = DB.DataBase([settings.GEO_TABLE, settings.CITY_TABLE,
                      settings.STREET_TABLE])
    parser = GeoParser(db)

    print(*parser.parse("Екатеринбург Тургенева 4"), sep='\n')
