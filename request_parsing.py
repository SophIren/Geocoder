import re
from typing import Set
from database_scripts import DB
import settings


class GeoParser:
    def __init__(self, db: DB.DataBase):
        self.db = db
        self.street_kinds = self.extract_street_kinds()

    @staticmethod
    def extract_street_kinds() -> Set[str]:
        with open(settings.STREET_KINDS_PATH, 'r', encoding='utf-8') as f:
            street_kinds = [line.strip() for line in f.readlines()]
        print(street_kinds)
        return set(street_kinds)

    @staticmethod
    def return_most_suitable(a, tokens):
        res = ''
        occurrences_dict = {}
        for elem in a:
            words = elem[1].split()
            if len(words) > 1:
                for word in words:
                    if word in tokens:
                        if elem not in occurrences_dict:
                            occurrences_dict[elem] = 1
                        else:
                            occurrences_dict[elem] += 1
            else:
                occurrences_dict[elem] = 1
        occurrences_dict = dict(sorted(occurrences_dict.items(), key=lambda item: item[1], reverse=True))
        i = occurrences_dict[list(occurrences_dict.keys())[0]]

        variations = []
        for elem in occurrences_dict:
            if occurrences_dict[elem] < i:
                break
            else:
                variations.append(elem[1])

        if len(variations) == 1:
            res = variations[0]
        else:
            min_dif = 100
            for elem in variations:
                if min_dif > abs(len(re.split("[;,./ ]", elem)) - len(tokens)):
                    res = elem
                    min_dif = abs(len(elem.split()) - len(tokens))
        return res

    def remove_additional_words(self, tokens):
        for token in tokens:
            if token.lower() in self.street_kinds:
                tokens.remove(token)

    def parse(self, line: str):
        tokens = re.split("[;,. ]", line)

        city = None
        street = None
        house = None

        for i in range(len(tokens), 0, -1):
            if tokens[i - 1][0].isdigit():
                house = ' '.join(tokens[i - 1:])
                tokens = tokens[:i - 1]
                break
        if not house:
            raise IndexError

        self.remove_additional_words(tokens)

        index = 0
        while not city:
            token = tokens[index]
            try:
                cities = self.db.filter_by_values(settings.CITY_TABLE, {
                    settings.GEO_PARAM_NAMES.city: token})
                city = self.return_most_suitable(cities, tokens)
            except IndexError:
                pass
            if city:
                for elem in city.split():
                    try:
                        tokens.remove(elem)
                    except ValueError:
                        pass
            else:
                index += 1
        for token in tokens:
            if street is None:
                try:
                    streets = self.db.filter_by_values(settings.STREET_TABLE, {
                        settings.GEO_PARAM_NAMES.street: token})
                    street = self.return_most_suitable(streets, tokens)
                except IndexError:
                    pass
                if street:
                    break

        if city is None or street is None or house is None:
            raise IndexError

        values = {
            settings.GEO_PARAM_NAMES.city: city,
            settings.GEO_PARAM_NAMES.street: street,
            settings.GEO_PARAM_NAMES.house: house
        }
        return list(self.db.filter_by_values(settings.GEO_TABLE, values))
        # sort by street kind (if specified) and housenumber

# if __name__ == "__main__":
#     db = DB.DataBase([settings.GEO_TABLE, settings.CITY_TABLE,
#                       settings.STREET_TABLE])
#     parser = GeoParser(db)
#
#     print(*parser.parse("Екатеринбург Тургенева 4"), sep='\n')
