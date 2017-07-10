#!/usr/bin/env python
# -*- coding: utf-8 -*-



import sys
import os

import unittest
import json
import re
import os
import math
import mock
import adsputils
from mock import patch
from io import BytesIO
from datetime import datetime
from sqlalchemy import create_engine
from reader import ADSClassicInputStream
from adsputils import ADSCelery
from row_view import SqlSync

class TestImport(unittest.TestCase):
    """
    Tests the appliction's methods
    """
    def setUp(self):
        
        unittest.TestCase.setUp(self)
        self.sync = SqlSync('test', {'INGEST_DATABASE': 'postgresql+psycopg2://docker:docker@localhost:6432/speedtest2'})
        self.sync.create_column_tables()
        
        self.proj_home = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        self.huge_file = self.proj_home + '/tests/data/generate_bigfile.tab'
        self.app = ADSCelery('test', local_config=\
            {
            'SQLALCHEMY_URL': 'postgresql+psycopg2://docker:docker@localhost:6432/speedtest2',
            'SQLALCHEMY_ECHO': False,
            'PROJ_HOME' : self.proj_home,
            'TEST_DIR' : os.path.join(self.proj_home, 'adsmp/tests'),
            })
    
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.app.close_app()
        self.sync.drop_column_tables()

    
    def test(self):
        with ADSClassicInputStream(self.huge_file) as f:    
            conn = self.app._engine.raw_connection()
            cursor = conn.cursor()
            #cursor.execute('ALTER TABLE test.relevance DROP CONSTRAINT "relevance_pkey"')
            #cursor.execute('drop index test.relevance_pkey')
            #conn.commit()
            cmd = 'COPY test.relevance(bibcode, boost, citation_count, read_count, norm_cites) FROM STDIN WITH (FORMAT TEXT, HEADER FALSE)'
            cursor.copy_expert(cmd, f)
            conn.commit()
            #cursor.execute('ALTER TABLE test.relevance ADD PRIMARY KEY(bibcode)')
            #conn.commit()

if __name__ == '__main__':
    unittest.main()