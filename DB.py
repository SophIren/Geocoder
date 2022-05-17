import sqlite3
import settings
from table import Table
from typing import List, Dict


class DataBase:
    def __init__(self, tables: List[Table], path: str = settings.DB_PATH):
        """ Инициализация БД """

        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.tables = tables
        for table in tables:
            self.create_table(table)

    def close(self):
        """ Разрывает соединение с БД """

        if self.cursor is not None:
            self.cursor.close()

        if self.conn is not None:
            self.conn.close()

    def get_table_by_name(self, name: str):
        for table in self.tables:
            if table.name == name:
                return table

    def create_table(self, table: Table):
        """ Создание таблицы """

        query = f"""CREATE TABLE IF NOT EXISTS {table.name}
        (id int primary key,"""

        param_queries = []
        for param in table.params:
            param_queries.append(f"""{param.name} {param.type}""")
        query += ','.join(param_queries) + ')'

        self.cursor.execute(query)
        self.conn.commit()

    def add_entries(self, table: Table, entries: List[tuple]):
        """ Добавление записи в таблицу """

        query = f"""INSERT OR REPLACE INTO {table.name} 
        VALUES({"?, " * (table.param_number - 1)}?)"""

        self.cursor.executemany(query, entries)
        self.conn.commit()

    def get_entries_by_column(self, table: Table, col: str, limit: int = None):
        query = f"SELECT {col} FROM {table.name}"
        if limit is not None:
            query = f"SELECT {col} FROM {table.name} LIMIT {limit}"

        return self.cursor.execute(query).fetchall()

    def filter_by_values(self, table: Table, values: Dict[str, str],
                         ignore_case=True):
        query = f"SELECT * FROM {table.name} WHERE "

        param_queries = []
        for param_name in values:
            param_query = f"{param_name} LIKE '%{values[param_name]}%'"
            if ignore_case:
                param_query = f"LOWER({param_name}) LIKE " \
                              f"LOWER('%{values[param_name]}%')"
            param_queries.append(param_query)
        query += ' AND '.join(param_queries)

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def found_any_by_values(self, table: Table, values: Dict[str, str],
                            ignore_case=True) -> bool:
        return bool(self.filter_by_values(table, values, ignore_case))

# if __name__ == "__main__":
#     db = DataBase()
#     db.close()
