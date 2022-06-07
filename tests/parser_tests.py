import unittest

from database_scripts import DB
import settings
from app.request_parsing import GeoParser


class TestSum(unittest.TestCase):
    def setUp(self):
        self.db = DB.DataBase([settings.GEO_TABLE, settings.CITY_TABLE,
                               settings.STREET_TABLE])
        self.parser = GeoParser(self.db)

    def test_len_simple_address(self):
        self.assertEqual(len(self.parser.parse("Екатеринбург Тургенева 4")),
                         2, "Should be 2")

    def test_different_city_positions(self):
        self.assertEqual(self.parser.parse("Екатеринбург Тургенева 4"),
                         self.parser.parse("Тургенева Екатеринбург 4"))

    def test_many_words_city(self):
        self.assertEqual(self.parser.parse("Великий Новгород Германа 19"),
                         [(288467214, 58.5306106,
                           31.2577717, 'Великий Новгород',
                           'улица Германа', '19', None),
                          (208561708, 58.530685260000006, 31.25735618,
                           'Великий Новгород', 'улица Германа', '19А', None)])

    def test_many_words_street(self):
        self.assertEqual(self.parser.parse("Пермь улица Аркадия Гайдара 2")[0],
                         (311500427, 58.0048728, 56.2932867, 'Пермь',
                          'улица Аркадия Гайдара', '2', None))

    def test_many_words_address(self):
        self.assertEqual(self.parser.parse("Великие Луки"
                                           " улица Карла Либкнехта 7/1"),
                         [(912961362, 56.3423151, 30.5188398, 'Великие Луки',
                           'улица Карла Либкнехта', '7/1', None),
                          (941384283, 56.3421914, 30.5186291, 'Великие Луки',
                           'улица Карла Либкнехта', '7/1', None)])

    def test_quotes_city(self):
        self.assertEqual(self.parser.parse("СНТ «Здоровье» 2-я улица 17"),
                         [(2214742489, 45.0177346, 38.9450186,
                           'СНТ «Здоровье»', '2-я улица', '17', None)])

    def test_important_street_type(self):
        self.assertEqual(self.parser.parse("Краснодар улица"
                                           " 40 лет Победы 14/1")[0],
                         (344162407, 45.0545536, 38.9962516, 'Краснодар',
                          'улица 40 лет Победы', '14/1', None))

    def test_hyphen_city(self):
        self.assertEqual(self.parser.parse("Санкт-Петербург 2-я"
                                           " Красноармейская улица 9/3"),
                         [(291553157, 59.9153967, 30.3132049,
                           'Санкт-Петербург',
                           '2-я Красноармейская улица', '9/3', None)])

    def test_prepositions_address(self):
        self.assertEqual(self.parser.parse("Ростов-на-Дону "
                                           "проспект 40-летия Победы 55"),
                         [(268001409, 47.2388683, 39.8114854, 'Ростов-на-Дону',
                           'проспект 40-летия Победы', '55', None),
                          (80861003, 47.2388058, 39.81080497999999,
                           'Ростов-на-Дону',
                           'проспект 40-летия Победы', '55Е', None)])

    def test_len_without_house_address(self):
        self.assertEqual(len(self.parser.parse("Ростов-на-Дону проспект"
                                               " 40-летия Победы")), 26)

    def test_wrong_city_address(self):
        with self.assertRaises(IndexError):
            self.parser.parse("Растов проспект 40-летия Победы 2")

    def test_wrong_street_address(self):
        with self.assertRaises(IndexError):
            self.parser.parse("Екатеринбург Тергенева 4")


if __name__ == '__main__':
    unittest.main()
