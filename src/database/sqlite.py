#!/usr/bin/env python
# Author: Geoffrey Golliher (brokenway@gmail.com)

from sqlite3 import dbapi2 as sqlite3
from abc_driver import AbstractDBDriver

class SQLite(AbstractDBDriver):
    def __init__(self, database):
        self.database = database
        self.conn = None

    def connect_db(self):
        """Connects to the specific database."""
        rv = sqlite3.connect(self.database)
        self.conn = rv
        rv.row_factory = sqlite3.Row
        return rv

    def init_db(self, app):
        """Initializes the database."""
        db = self.connect_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

    @staticmethod
    def last_id(cur):
        return cur.lastrowid

    @staticmethod
    def transform_shorties(shorties):
        return shorties

    def close(self):
        self.conn.close()
