import unittest

from database_scripts import DB
import settings
from request_parsing import GeoParser


class TestSum(unittest.TestCase):
    def setUp(self):
        self.db = DB.DataBase([settings.GEO_TABLE, settings.CITY_TABLE,
                               settings.STREET_TABLE])
        self.parser = GeoParser(self.db)

    def test_len_simple_address(self):
        print(self.parser.parse("Екатеринбург Тургенева 4"))
        self.assertEqual(len(self.parser.parse("Екатеринбург Тургенева 4")),
                         2, "Should be 2")


if __name__ == '__main__':
    unittest.main()
