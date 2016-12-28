#!/usr/bin/env python
# Author: Geoffrey Golliher (ggolliher@katch.com)

import psycopg2

from abc_driver import AbstractDBDriver

class Postgres(AbstractDBDriver):
    def __init__(self, app, port=5432, host='localhost',
                 password='ou812', user='postgres'):
        self.conn = None 
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.app = app

    def connect_db(self):
        self.conn = psycopg2.connect(
                host=self.host,user=self.user,
                password=self.password,port=self.port)
        return self.conn

    def cur(self):
        return self.conn.cursor()

    def init_db(self, app, create=False):
        db = self.connect_db()
        self.cur().execute('END;')
        if create == True:
            self.cur().execute('create database shorties;')
        with app.open_resource('postgres_schema.sql', mode='r') as f:
            self.cur().execute(f.read())

    @staticmethod
    def last_id(cur):
        return cur.fetchone()[0]

    @staticmethod
    def transform_shorties(shorties):
        return [{'url':d[1], 'key':d[2], 'owner': d[3]} for d in shorties]
