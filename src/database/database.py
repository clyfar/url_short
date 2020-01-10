#!/usr/bin/env python
# Author: Geoffrey Golliher (brokenway@gmail.com)

import sqlite 
import postgres

class Database(object):

    def __init__(self, db_type, app):
        self.db_type = db_type
        self.app = app
        self.DATABASE_HASH = {
                'sqlite': sqlite.SQLite,
                'postgres': postgres.Postgres}

    def pickAndReturn(self, database_path):
        return self.DATABASE_HASH[self.db_type](database_path)
