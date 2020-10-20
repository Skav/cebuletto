import mysql.connector
import os

class BasicModel:

    def __init__(self, table_name):
        self._db = mysql.connector.connect(user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
                                           host=os.getenv("DB_HOST"), database=os.getenv("DB_NAME"))
        self._cursor = self._db.cursor(dictionary=True)
        self.__table_name = table_name
        self.__id_table = self.__get_primary_table_name()

    def __del__(self):
        self._db.close()

    def __get_primary_table_name(self):
        self._cursor.execute(f"SHOW KEYS FROM {self.__table_name} WHERE Key_name = 'PRIMARY'")
        return self._cursor.fetchone()['Column_name']

    def get_all(self, limit=1000):
        query = f"SELECT * FROM {self.__table_name} LIMIT %s"
        self._cursor.execute(query, (limit,))
        return self._cursor.fetchall()

    def get_row_by_id(self, row_id: int):
        query = f"SELECT * FROM {self.__table_name} WHERE {self.__id_table} = %s LIMIT 1"
        self._cursor.execute(query, (row_id,))
        return self._cursor.fetchone()

    def delete_row_by_id(self, row_id: int):
        query = f"DELETE FROM {self.__table_name} WHERE {self.__id_table} = %s"
        self._cursor.execute(query, (row_id,))
        self._db.commit()
