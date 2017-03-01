# -*- coding: utf-8 -*-

from decouple import config
from shortener_url.extensions import gettext

class Config(object):
    
    BOOTSTRAP_SERVE_LOCAL = True
    TEMPLATES_AUTO_RELOAD = True
    
    SESSION_PROTECTION = 'strong'

    DB_SETTINGS = {
        'host': config('SHORTURL_DB_URL', 'mongodb://mongo/shorturl'),
        'db': 'shorturl'
    }        
    
    SECRET_KEY = config('SHORTURL_SECRET_KEY', 'very very secret key key key')
    
    DEBUG = config('SHORTURL_DEBUG', False, cast=bool)
        
    SENTRY_DSN = config('SHORTURL_SENTRY_DSN', None)
    
    #---Flask-Babel
    TIMEZONE = "UTC"#"Europe/Paris" 
    DEFAULT_LANG = "fr"
    ACCEPT_LANGUAGES = ['en', 'fr']
    
    ACCEPT_LANGUAGES_CHOICES = (
        ('en', gettext('English')),
        ('fr', gettext('French')),
    )
    
    BABEL_DEFAULT_LOCALE = DEFAULT_LANG
    BABEL_DEFAULT_TIMEZONE = TIMEZONE
    
    RECAPTCHA2_SITEKEY = config('SHORTURL_RECAPTCHA2_SITEKEY', None)
    RECAPTCHA2_SECRETKEY = config('SHORTURL_RECAPTCHA2_SECRETKEY', None)
    
    MAIL_ADMINS = config('SHORTURL_MAIL_ADMIN', "root@localhost.com")
    
    #---Flask-Mail
    MAIL_SERVER = config('SHORTURL_MAIL_SERVER', "127.0.0.1")
    MAIL_PORT = config('SHORTURL_MAIL_PORT', 25, cast=int)
    MAIL_USE_TLS = config('SHORTURL_MAIL_USE_TLS', False, cast=bool)
    MAIL_USE_SSL = config('SHORTURL_MAIL_USE_SSL', False, cast=bool)
    #MAIL_DEBUG : default app.debug
    MAIL_USERNAME = config('SHORTURL_MAIL_USERNAME', None)
    MAIL_PASSWORD = config('SHORTURL_MAIL_PASSWORD', None)
    MAIL_DEFAULT_SENDER = config('SHORTURL_MAIL_DEFAULT_SENDER', "root@localhost.com")
    MAIL_MAX_EMAILS = None
    #MAIL_SUPPRESS_SEND : default app.testing
    MAIL_ASCII_ATTACHMENTS = False
    LOGGING_MAIL_ENABLE = config('SHORTURL_LOGGING_MAIL_ENABLE', False, cast=bool)
    
    #---Flask-Assets
    FLASK_ASSETS_USE_CDN = False
    FLASK_ASSETS_DEBUG = False
    FLASK_ASSETS_URL_EXPIRE = True
    
    #---Flask-Admin
    FLASK_ADMIN_SWATCH = config('SHORTURL_FLASK_ADMIN_SWATCH', "darkly")
    
    #---Flask-Login
    #LOGIN_DISABLED = False
    
    #---Flask Security
    SECURITY_PASSWORD_SALT = "abc"
    # SECURITY_PASSWORD_HASH = "bcrypt"  # requires py-bcrypt
    # SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
    SECURITY_PASSWORD_HASH = "plaintext"
    SECURITY_EMAIL_SENDER = "support@example.com"
    SECURITY_CONFIRMABLE = False
    SECURITY_REGISTERABLE = False
    SECURITY_RECOVERABLE = False
    SECURITY_CHANGEABLE = False
    SECURITY_CONFIRM_SALT = "570be5f24e690ce5af208244f3e539a93b6e4f05"
    SECURITY_REMEMBER_SALT = "de154140385c591ea771dcb3b33f374383e6ea47"
    SECURITY_DEFAULT_REMEMBER_ME = True

        
class Prod(Config):
    pass

class Dev(Config):
    
    BOOTSTRAP_USE_MINIFIED = False

    DEBUG = True

    SECRET_KEY = 'dev_key'
    
    MAIL_DEBUG = True
    
class Test(Config):

    DB_SETTINGS = {
        'host': config('SHORTURL_DB_URL', 'mongodb://mongo/shorturl_test'),
        'db': 'shorturl_test'
    }        
    COUNTERS_ENABLE = False

    TESTING = True    
    
    SECRET_KEY = 'test_key'
    
    WTF_CSRF_ENABLED = False
    
    PROPAGATE_EXCEPTIONS = True
    
    CACHE_TYPE = "null"
    
    MAIL_SUPPRESS_SEND = True
    

class Custom(Config):
    pass

