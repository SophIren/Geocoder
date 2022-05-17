import re
from typing import Set
import DB
import settings


class GeoParser:
    def __init__(self, db: DB.DataBase):
        self.db = db
        self.geo_table = self.db.get_table_by_name(settings.GEO_TABLE_NAME)
        self.street_kinds = self.extract_street_kinds()

    def extract_street_kinds(self) -> Set[str]:
        streets = self.db.get_entries_by_column(
            self.geo_table,
            settings.PARAM_NAMES.street,
            settings.EXTRACT_STREET_KINDS_LIMIT
        )
        street_kinds = set()

        for street in streets:
            for word in re.split("[/. ]", street[0]):
                if word and word[0].islower():
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
            if self.db.found_any_by_values(
                    self.geo_table, {settings.PARAM_NAMES.city: token}
            ):
                city = token
            elif self.db.found_any_by_values(
                    self.geo_table, {settings.PARAM_NAMES.street: token}
            ):
                street = token
            elif self.db.found_any_by_values(
                    self.geo_table, {settings.PARAM_NAMES.house: token}
            ):
                house = token

        values = {
            settings.PARAM_NAMES.city: city,
            settings.PARAM_NAMES.street: street,
            settings.PARAM_NAMES.house: house
        }
        return list(self.db.filter_by_values(self.geo_table, values))


if __name__ == "__main__":
    db = DB.DataBase([settings.GEO_TABLE])
    parser = GeoParser(db)

    print(*parser.parse("Магнитогорск карла 174"), sep='\n')

