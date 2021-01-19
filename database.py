import os
import sqlite3
from sqlite3 import Error


class DataBase:
    def __init__(self, db_file=None):
        if not db_file:
            local_dir = os.path.dirname(__file__)
            db_file = os.path.join(local_dir, 'friends_list.db')
        self.db_file = db_file
        self.connection = None
        self.create_connection()

    def create_connection(self):
        """ create a database connection to a SQLite database """
        try:
            self.connection = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)

    def make_sql_command(self, sql, data_list):
        cur = self.connection.cursor()
        cur.execute(sql, data_list)
        self.connection.commit()

    def querying_data(self, sql, data_list=None):
        cur = self.connection.cursor()
        if data_list:
            cur.execute(sql, data_list)
        else:
            cur.execute(sql)
        rows = cur.fetchall()
        return rows

    def create_table(self, create_table_sql):
        try:
            c = self.connection.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)
