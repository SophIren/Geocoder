import unittest
import sqlite3
from typing import List

from database_scripts import DB
from database_scripts import parameter
import settings


class TestDataBase(unittest.TestCase):
    def setUp(self):
        self.db = DB.DataBase([settings.GEO_TABLE, settings.CITY_TABLE,
                               settings.STREET_TABLE], settings.TEST_DB_NAME)
        self.conn = sqlite3.connect(settings.TEST_DB_NAME,
                                    check_same_thread=False)
        self.cursor = self.conn.cursor()

        query = f"""INSERT OR REPLACE INTO {settings.CITY_TABLE.name}
                VALUES({"?, " * settings.CITY_TABLE.param_number}?)"""
        self.cursor.executemany(query, [(1, "УХТЫ"), (2, "ГОРЫ"), (3, "ПУПА"),
                                        (4, "ПУПА")])

        query = f"""INSERT OR REPLACE INTO {settings.GEO_TABLE.name}
                        VALUES({"?, " * settings.GEO_TABLE.param_number}?)"""
        self.cursor.executemany(query,
                                [(1, 3, 5, "ПУПА", "ЛУПОВСКАЯ", "1", None),
                                 (2, 5, 3, "ПУПА", "УХТОВСКАЯ", "10", None)])

        self.conn.commit()

    def test_created_tables(self):
        self.cursor.execute(
            f"SELECT name FROM sqlite_master WHERE "
            f"type='table'")
        tables = list(map(lambda el: el[0], self.cursor.fetchall()))

        self.assertIn(settings.CITY_TABLE.name, tables)
        self.assertIn(settings.STREET_TABLE.name, tables)
        self.assertIn(settings.GEO_TABLE.name, tables)

    @staticmethod
    def get_db_param_list(params: List[parameter.Parameter]):
        param_list = [(0, 'id', 'int', 0, None, 1)]
        for i in range(len(params)):
            param_list.append((i + 1, params[i].name, params[i].type, 0,
                               params[i].default, 0))
        return param_list

    def test_created_table_columns(self):
        geo_table_info = self.cursor.execute(
            f'PRAGMA table_info({settings.GEO_TABLE.name})').fetchall()
        city_table_info = self.cursor.execute(
            f'PRAGMA table_info({settings.CITY_TABLE.name})').fetchall()
        street_table_info = self.cursor.execute(
            f'PRAGMA table_info({settings.STREET_TABLE.name})').fetchall()

        self.assertEqual(geo_table_info,
                         self.get_db_param_list(settings.GEO_TABLE.params))
        self.assertEqual(city_table_info,
                         self.get_db_param_list(settings.CITY_TABLE.params))
        self.assertEqual(street_table_info,
                         self.get_db_param_list(settings.STREET_TABLE.params))

    def test_add_entries(self):
        self.db.add_entries(settings.CITY_TABLE, [(1, "ЕКБ"), (2, "МГН")])
        entries = self.cursor.execute(
            f"SELECT * FROM {settings.CITY_TABLE.name}").fetchall()
        self.assertIn((1, "ЕКБ"), entries)
        self.assertIn((2, 'МГН'), entries)

    def test_get_entries_by_column(self):
        actual = self.cursor.execute(f'SELECT '
                                     f'{settings.GEO_PARAM_NAMES.city} '
                                     f'FROM {settings.CITY_TABLE.name}') \
            .fetchall()
        supposed = self.db.get_entries_by_column(settings.CITY_TABLE,
                                                 settings.GEO_PARAM_NAMES.city)
        self.assertEqual(actual, supposed)

    def test_get_entries_by_column_distinct(self):
        supposed = self.db.get_entries_by_column(settings.CITY_TABLE,
                                                 settings.GEO_PARAM_NAMES.city,
                                                 distinct=True)
        self.assertEqual([('УХТЫ',), ('ГОРЫ',), ('ПУПА',)], supposed)

    def test_get_entries_by_column_limit(self):
        supposed = self.db.get_entries_by_column(settings.CITY_TABLE,
                                                 settings.CITY_TABLE.params[0]
                                                 .name, limit=2)
        self.assertEqual([('УХТЫ',), ('ГОРЫ',)], supposed)

    def test_get_similar_entries(self):
        supposed = self.db.get_similar_entries(settings.GEO_TABLE, {
            settings.GEO_PARAM_NAMES.city: "ПУПА",
            settings.GEO_PARAM_NAMES.street: "ЛУП"
        })
        self.assertEqual(supposed,
                         [(1, 3.0, 5.0, 'ПУПА', 'ЛУПОВСКАЯ', '1', None)])

    def test_get_similar_entries_contains(self):
        supposed = self.db.get_similar_entries(settings.GEO_TABLE, {
            settings.GEO_PARAM_NAMES.city: "ПУПА",
            settings.GEO_PARAM_NAMES.street: "ОВСКАЯ"
        })
        self.assertEqual(supposed,
                         [(1, 3.0, 5.0, 'ПУПА', 'ЛУПОВСКАЯ', '1', None),
                          (2, 5.0, 3.0, 'ПУПА', 'УХТОВСКАЯ', '10', None)])
