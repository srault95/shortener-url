# -*- coding: utf-8 -*-

from flask import json
from flask import current_app
from flask_login import user_logged_in, user_logged_out, user_unauthorized
from flask_security import url_for_security

from flask_testing import TestCase

from shortener_url import wsgi

def clean_mongo():
    models = current_app.models
    models.SocialConnection.drop_collection()
    models.User.drop_collection()
    models.Role.drop_collection()
    models.URL.drop_collection()
    models.URLStat.drop_collection()
    
def clean_peewee(models):
    raise NotImplementedError()    

JSON_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

class BaseTest(TestCase):
    
    def setUp(self):
        self.clean_db()
        self.current_user = None
        user_logged_in.connect(self._signal_login)
        user_logged_out.connect(self._signal_logout)

    def create_app(self):
        app = wsgi.create_app('shortener_url.settings.Test')
        
        print("DB_SETTINGS : ", app.config["DB_SETTINGS"])
        
        self.clean_db = None
        
        if app.config['STORAGE'] == "mongo":
            self.clean_db = clean_mongo
            
        elif app.config['STORAGE'] == "sql":
            self.clean_db = clean_peewee
        
        return app

    def security_url(self):
        return {
            'login': url_for_security('login'),
            'logout': url_for_security('logout'),
            #'loginbyapikey': url_for('auth.loginbyapikey')
        }

    def _signal_login(self, sender, user=None):
        print("_signal_login !!!!!!!!!!!")
        self.current_user = user

    def _signal_logout(self, sender, user=None):
        self.current_user = None

    def logout(self, url=None):
        url = url or self.security_url()['logout']
        return self.client.get(url)

    def json_post(self, url=None, dict_data=None, headers={}, follow_redirects=True):
        data=json.dumps(dict_data)
        headers.update(JSON_HEADERS)
        return self.client.post(url, headers=headers, data=data, follow_redirects=follow_redirects)

    def json_get(self, url=None, headers={}, follow_redirects=True):
        headers.update(JSON_HEADERS)
        return self.client.get(url, headers=headers, follow_redirects=follow_redirects)


    def assertContentType(self, response, content_type):
        """Assert the content-type of a Flask test client response

        :param response: The test client response object
        :param content_type: The expected content type
        """
        self.assertEquals(content_type, response.headers['Content-Type'])
        return response
        
    def assertJson(self, response):
        """Test that content returned is in JSON format

        :param response: The test client response object
        """
        try:
            json.loads(response.data)
        except Exception as err:
            msg = "error: %s - data: %s" % (str(err), getattr(response, 'data', ''))
            return self.fail(msg)
        
        return self.assertContentType(response, 'application/json')

    def get_current_user(self):
        return self.current_user

    def assertIsAuthenticated(self, username=None):
        
        user = self.get_current_user()

        self.assertIsNotNone(user)
        
        if username:
            self.assertEqual(getattr(user, 'username'), username)

    def assertIsNotAuthenticated(self):
        
        #TODO: vérifier si Anonymous ?
        
        self.assertIsNone(self.get_current_user())
