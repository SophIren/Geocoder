import re
from typing import Set, List
from database_scripts import DB
import settings


class GeoParser:
    PREPOSITION_WORDS = ['на', 'я', 'й', 'летия']

    def __init__(self, db: DB.DataBase):
        self.has_additional_word = None
        self.db = db
        self.street_kinds = self.extract_street_kinds()
        self.city_kinds = self.extract_city_kinds()

    @staticmethod
    def extract_street_kinds() -> Set[str]:
        with open(settings.STREET_KINDS_PATH, 'r', encoding='utf-8') as f:
            street_kinds = [line.strip() for line in f.readlines()]
        return set(street_kinds)

    @staticmethod
    def extract_city_kinds() -> Set[str]:
        with open(settings.CITY_KINDS_PATH, 'r', encoding='utf-8') as f:
            city_kinds = [line.strip() for line in f.readlines()]
        return set(city_kinds)

    @staticmethod
    def get_token_occurrences(toponym, tokens_with_additional_words):
        lower_tokens = [elem.lower() for elem in tokens_with_additional_words]
        occurrences = {}
        for elem in toponym:
            words = elem[1].split()
            if len(words) > 1:
                for word in words:
                    if word.lower() in lower_tokens:
                        if elem not in occurrences:
                            occurrences[elem] = 1
                        else:
                            occurrences[elem] += 1
            else:
                occurrences[elem] = 1
        return dict(sorted(occurrences.items(),
                           key=lambda item: item[1], reverse=True))

    @staticmethod
    def return_most_suitable(toponym, tokens_with_additional_words):
        res = ''
        occurrences_dict = GeoParser.get_token_occurrences(
            toponym,
            tokens_with_additional_words)
        max_matches_count = occurrences_dict[list(occurrences_dict.keys())[0]]

        variations = []
        for elem in occurrences_dict:
            if occurrences_dict[elem] < max_matches_count:
                break
            variations.append(elem[1])

        if len(variations) == 1:
            return variations[0]

        min_dif = 1000
        for variation in variations:
            variation_len = len(re.split("[;,./ ]", variation))
            if min_dif > abs(variation_len - max_matches_count):
                res = variation
                min_dif = abs(variation_len - max_matches_count)
        return res

    def remove_additional_words(self, tokens):
        index = 0
        self.has_additional_word = False
        while index != len(tokens):
            if tokens[index].lower() in self.street_kinds:
                tokens.remove(tokens[index])
                self.has_additional_word = True
            elif not tokens[index] or tokens[index].lower() in self.city_kinds:
                tokens.remove(tokens[index])
            else:
                index += 1

    @staticmethod
    def to_normal_case(token: str):
        index = 0
        token = token.lower()
        if "-" in token:
            res = []
            for elem in token.split("-"):
                if elem not in GeoParser.PREPOSITION_WORDS:
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

    @staticmethod
    def extract_building(tokens: List[str]):
        house_tokens = []
        while not tokens[-1][0].isdigit():
            house_tokens.append(tokens.pop())

        house_tokens.append(tokens.pop())
        return ' '.join(house_tokens)

    def extract_city(self, tokens: List[str], tokens_with_additional_words):
        index = 0
        city = None
        while not city:
            token = tokens[index]
            try:
                cities = self.db.get_similar_entries(
                    settings.CITY_TABLE, {settings.GEO_PARAM_NAMES.city: token})
                city = self.return_most_suitable(
                    cities, tokens_with_additional_words)
            except IndexError:
                pass

            index += 1

        for elem in city.split():
            try:
                tokens.remove(elem)
                tokens_with_additional_words.remove(elem)
            except ValueError:
                pass

        return city

    def extract_street(self, tokens: List[str], tokens_with_additional_words):
        street = None
        for token in tokens:
            if street is None:
                try:
                    streets = self.db.get_similar_entries(
                        settings.STREET_TABLE,
                        {settings.GEO_PARAM_NAMES.street: token})
                    street = self.return_most_suitable(
                        streets,
                        tokens_with_additional_words)
                except IndexError:
                    pass
                if street and not self.has_additional_word:
                    street_words = street.split()
                    self.remove_additional_words(street_words)
                    street = ' '.join(street_words)

        return street

    def parse(self, line: str):
        line = re.split("[;,. ]", line)

        tokens_with_additional_words = list(map(self.to_normal_case, line))

        tokens = list(map(self.to_normal_case, line))
        self.remove_additional_words(tokens)

        house = GeoParser.extract_building(tokens)
        city = self.extract_city(tokens, tokens_with_additional_words)
        if not tokens:
            tokens.extend(house.split())
            tokens_with_additional_words.extend(house.split())
            house = None
        street = self.extract_street(tokens, tokens_with_additional_words)

        if city is None or street is None:
            raise IndexError

        values = {
            settings.GEO_PARAM_NAMES.city: city,
            settings.GEO_PARAM_NAMES.street: street
        }
        if house:
            values[settings.GEO_PARAM_NAMES.house] = house

        return list(self.db.get_similar_entries(settings.GEO_TABLE, values))
