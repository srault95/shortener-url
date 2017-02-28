# -*- coding: utf-8 -*-

from flask import url_for
from .base import BaseTest

class ApiTest(BaseTest):

    # nosetests -s -v shortener_url.tests.functionals.test_api:ApiTest

    def test_auth_apikey(self):
        
        # nosetests -s -v shortener_url.tests.functionals.test_api:ApiTest.test_auth_apikey
        
        api_key = "x1"
        
        self.app.models.User._create(email="user@domain.net", 
                                     api_key=api_key)
        self.assertIsAuthenticated()
        
        origin = "http://www.domain.net/index.html"
        url = "%s?url=%s&key=%s&json=1" % (url_for("api.create"), origin, api_key)
        response = self.json_post(url)
        
        self.assertJson(response)
        self.assertEquals(response.json, "4SnLWw")
    
    def test_create_url(self):
        self.fail("Not Implemented")

    def test_create_exist_url(self):
        self.fail("Not Implemented")

    def test_create_invalid_url_format(self):
        self.fail("Not Implemented")

    def test_create_urls(self):
        self.fail("Not Implemented")

    def test_delete_url(self):
        self.fail("Not Implemented")

    def test_delete_urls(self):
        self.fail("Not Implemented")

    def test_update_url(self):
        self.fail("Not Implemented")

    def test_update_url_not_found(self):
        self.fail("Not Implemented")

    def test_update_urls(self):
        self.fail("Not Implemented")

    def test_update_urls_not_found(self):
        self.fail("Not Implemented")
