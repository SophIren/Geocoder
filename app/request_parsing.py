import re
from typing import Set
from database_scripts import DB
import settings


class GeoParser:
    def __init__(self, db: DB.DataBase):
        self.has_additional_word = None
        self.db = db
        self.street_kinds = self.extract_street_kinds()

    @staticmethod
    def extract_street_kinds() -> Set[str]:
        with open(settings.STREET_KINDS_PATH, 'r', encoding='utf-8') as f:
            street_kinds = [line.strip() for line in f.readlines()]
        return set(street_kinds)

    @staticmethod
    def return_most_suitable(a, tokens_with_additional_words):
        res = ''
        lower_tokens = [elem.lower() for elem in tokens_with_additional_words]
        occurrences_dict = {}
        for elem in a:
            words = elem[1].split()
            if len(words) > 1:
                for word in words:
                    if word.lower() in lower_tokens:
                        if elem not in occurrences_dict:
                            occurrences_dict[elem] = 1
                        else:
                            occurrences_dict[elem] += 1
            else:
                occurrences_dict[elem] = 1
        occurrences_dict = dict(sorted(occurrences_dict.items(),
                                       key=lambda item: item[1], reverse=True))
        max_matches_count = occurrences_dict[list(occurrences_dict.keys())[0]]

        variations = []
        for elem in occurrences_dict:
            if occurrences_dict[elem] < max_matches_count:
                break
            else:
                variations.append(elem[1])

        if len(variations) == 1:
            res = variations[0]
        else:
            min_dif = 100
            for elem in variations:
                if min_dif > abs(len(re.split("[;,./ ]", elem))
                                 - max_matches_count):
                    res = elem
                    min_dif = abs(len(re.split("[;,./ ]", elem))
                                  - max_matches_count)
        return res

    def remove_additional_words(self, tokens):
        index = 0
        while index != len(tokens):
            if tokens[index].lower() in self.street_kinds or \
                    tokens[index] == "":
                tokens.remove(tokens[index])
                self.has_additional_word = True
            else:
                index += 1

    @staticmethod
    def to_normal_case(token: str):
        index = 0
        token = token.lower()
        if "-" in token:
            res = []
            for elem in token.split("-"):
                if elem not in ['на', 'я', 'й', 'летия']:
                    res.append(elem[0].upper() + elem[1:])
                else:
                    res.append(elem)
            return "-".join(res)
        try:
            if not token[index].isalpha():
                return token[0] + token[1].upper() + token[2:]
            return token[0].upper() + token[1:]
        except IndexError:
            return token

    def parse(self, line: str):
        tokens_with_additional_words = list(map(self.to_normal_case,
                                                re.split("[;,. ]", line)))

        city = None
        street = None
        house = None

        tokens = tokens_with_additional_words.copy()
        self.has_additional_word = False
        self.remove_additional_words(tokens)

        for i in range(len(tokens), 0, -1):
            if tokens[i - 1][0].isdigit():
                house = ' '.join(tokens[i - 1:])
                tokens = tokens[:i - 1]
                break
        if not house:
            # raise IndexError
            pass

        index = 0
        while not city:
            token = tokens[index]
            try:
                cities = self.db.get_similar_entries(settings.CITY_TABLE, {
                    settings.GEO_PARAM_NAMES.city: token})
                city = self.return_most_suitable(cities,
                                                 tokens_with_additional_words)
            except IndexError:
                pass
            if city:
                for elem in city.split():
                    try:
                        tokens.remove(elem)
                        tokens_with_additional_words.remove(elem)
                    except ValueError:
                        pass
            else:
                index += 1

        if not tokens:
            tokens.extend(house.split())
            tokens_with_additional_words.extend(house.split())
            house = None

        for token in tokens:
            token = token
            if street is None:
                try:
                    streets = \
                        self.db.get_similar_entries(settings.STREET_TABLE, {
                            settings.GEO_PARAM_NAMES.street: token})
                    street = self.return_most_suitable(
                        streets, tokens_with_additional_words)
                except IndexError:
                    pass
                if street and not self.has_additional_word:
                    street_words = street.split()
                    self.remove_additional_words(street_words)
                    street = ' '.join(street_words)

        if city is None or street is None:
            raise IndexError

        values = {
            settings.GEO_PARAM_NAMES.city: city,
            settings.GEO_PARAM_NAMES.street: street
        }
        if house:
            values[settings.GEO_PARAM_NAMES.house] = house
        return list(self.db.get_similar_entries(settings.GEO_TABLE, values))
        # sort by street kind (if specified) and housenumber

# if __name__ == "__main__":
#     db = DB.DataBase([settings.GEO_TABLE, settings.CITY_TABLE,
#                       settings.STREET_TABLE])
#     parser = GeoParser(db)
#
#     print(*parser.parse("Екатеринбург Тургенева 4"), sep='\n')
