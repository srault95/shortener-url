# -*- coding: utf-8 -*-

import unittest
from io import StringIO

class BaseTestCase(unittest.TestCase):
    
    def setUp(self):
        super().setUp()
        self.log = StringIO()        

    def assertInLog(self, msg):
        self.assertTrue(msg in self.log.getvalue())
        
    def assertNotInLog(self, msg):
        self.assertFalse(msg in self.log.getvalue())

