# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)

from decouple import config as config_from_env
from werkzeug.contrib.fixers import ProxyFix

from flask import Flask, request, abort, session, g, redirect, url_for, render_template, current_app, render_template_string
from flask import json
from flask_security import login_required

from shortener_url import extensions
from shortener_url import constants
from shortener_url import utils

def _conf_logging(debug=False, 
                  stdout_enable=True, 
                  syslog_enable=False,
                  prog_name='shortener_url',
                  config_file=None,
                  LEVEL_DEFAULT="INFO"):

    import sys
    import logging.config
    
    if config_file:
        logging.config.fileConfig(config_file, disable_existing_loggers=True)
        return logging.getLogger(prog_name)
    
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'debug': {
                'format': 'line:%(lineno)d - %(asctime)s %(name)s: [%(levelname)s] - [%(process)d] - [%(module)s] - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'simple': {
                'format': '%(asctime)s %(name)s: [%(levelname)s] - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },    
        'handlers': {
            'null': {
                'level':LEVEL_DEFAULT,
                'class':'logging.NullHandler',
            },
            'console':{
                'level':LEVEL_DEFAULT,
                'class':'logging.StreamHandler',
                'formatter': 'simple'
            },      
        },
        'loggers': {
            '': {
                'handlers': [],
                'level': 'INFO',
                'propagate': False,
            },
            prog_name: {
                #'handlers': [],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }
    
    if sys.platform.startswith("win32"):
        LOGGING['loggers']['']['handlers'] = ['console']

    elif syslog_enable:
        LOGGING['handlers']['syslog'] = {
                'level':'INFO',
                'class':'logging.handlers.SysLogHandler',
                'address' : '/dev/log',
                'facility': 'daemon',
                'formatter': 'simple'    
        }       
        LOGGING['loggers']['']['handlers'].append('syslog')
        
    if stdout_enable:
        if not 'console' in LOGGING['loggers']['']['handlers']:
            LOGGING['loggers']['']['handlers'].append('console')

    '''if handlers is empty'''
    if not LOGGING['loggers']['']['handlers']:
        LOGGING['loggers']['']['handlers'] = ['console']
    
    if debug:
        LOGGING['loggers']['']['level'] = 'DEBUG'
        LOGGING['loggers'][prog_name]['level'] = 'DEBUG'
        for handler in LOGGING['handlers'].keys():
            LOGGING['handlers'][handler]['formatter'] = 'debug'
            LOGGING['handlers'][handler]['level'] = 'DEBUG' 

    #from pprint import pprint as pp 
    #pp(LOGGING)
    #werkzeug = logging.getLogger('werkzeug')
    #werkzeug.handlers = []
             
    logging.config.dictConfig(LOGGING)
    logger = logging.getLogger(prog_name)
    
    return logger

def _conf_logging_mail(app):
    from logging.handlers import SMTPHandler
    
    ADMIN = app.config.get("MAIL_ADMINS", None)
    if not ADMIN:
        app.logger.error("Emails address for admins are not configured")
        return
        
    ADMINS = ADMIN.split(",")
    mail_handler = SMTPHandler(app.config.get("MAIL_SERVER"),
                               app.config.get("MAIL_DEFAULT_SENDER"),
                               ADMINS, 
                               'Application Failed')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler) 

def _conf_sentry(app):
    try:
        from raven.contrib.flask import Sentry
        if app.config.get('SENTRY_DSN', None):
            Sentry(app, logging=True, level=app.logger.level)
    except ImportError:
        pass

def _conf_compress(app):
    from flask_compress import Compress
    Compress(app)        

def _conf_mail(app):
    extensions.mail.init_app(app)

def _conf_jsonify(app):

    def jsonify(obj):
        content = json.dumps(obj)
        return current_app.response_class(content, mimetype='application/json')

    app.jsonify = jsonify
    
def _conf_errors(app):

    """
    from social_core.exceptions import SocialAuthBaseException
    #TODO: @app.errorhandler(500)
    def error_handler(error):
        if isinstance(error, SocialAuthBaseException):
            return redirect('/socialerror')    
    """
    @app.errorhandler(500)
    def error_500(error):
        is_json = request.args.get('json') or request.is_xhr
        values = dict(error="Server Error", original_error=error, referrer=request.referrer)
        if is_json:
            values['original_error'] = str(values['original_error'])
            return app.jsonify(values), 500
        return render_template('shortener_url/errors/500.html', **values), 500
    
    @app.errorhandler(403)
    @app.errorhandler(404)
    def not_found_error(error):
        is_json = request.args.get('json') or request.is_xhr
        values = dict(error="404 Error", original_error=error, referrer=request.referrer)
        if is_json:
            values['original_error'] = str(values['original_error'])
            return app.jsonify(values), 404
        return render_template('shortener_url/errors/404.html', **values), 404

def _conf_babel(app):
    '''Flask-Babel'''
    extensions.babel.init_app(app)        
    babel = extensions.babel
    
    #TODO: babel
    return
    
    #fr <class 'babel.core.Locale'>
    #for t in babel.list_translations():
    #    print t, type(t)
    
    #current = session.get(constants.SESSION_LANG_KEY, app.config.get('DEFAULT_LANG'))
    @app.before_request
    def set_locales():
        current_lang  = session.get(constants.SESSION_LANG_KEY, None)
        if not current_lang:
            session[constants.SESSION_LANG_KEY] = app.config.get('DEFAULT_LANG')

        current_tz  = session.get(constants.SESSION_TIMEZONE_KEY, None)
        if not current_tz:
            session[constants.SESSION_TIMEZONE_KEY] = app.config.get('TIMEZONE')
    
    @babel.localeselector
    def get_locale():
        current_lang  = session.get(constants.SESSION_LANG_KEY, app.config.get('DEFAULT_LANG'))
        return current_lang
        """
        if current_user.locale:
            return current_user.locale        
        default_locale = current_app.config.get('BABEL_DEFAULT_LOCALE', 'en')
        accept_languages = current_app.config.get('ACCEPT_LANGUAGES', [default_locale])
        return request.accept_languages.best_match(accept_languages)
        """
    
    @babel.timezoneselector
    def get_timezone():
        return session.get(constants.SESSION_TIMEZONE_KEY, app.config.get('TIMEZONE'))
        
        """
        if current_user.timezone:
            return current_user.timezone
        
        return current_app.config.get('BABEL_DEFAULT_TIMEZONE', 'UTC')
        """        

def _conf_bootstrap(app):
    '''Flask-Bootstrap'''
    from flask_bootstrap import Bootstrap
    Bootstrap(app)

def _conf_social(app):

    socials_found = {}
    
    GITHUB_KEY = config_from_env('SHORTURL_SOCIAL_GITHUB_KEY', None)
    GITHUB_SECRET = config_from_env('SHORTURL_SOCIAL_GITHUB_SECRET', None)
    
    if GITHUB_KEY and GITHUB_SECRET:
        socials_found["flask_social_blueprint.providers.Github"] = {
            'consumer_key': GITHUB_KEY,
            'consumer_secret': GITHUB_SECRET
        }

    app.config['SOCIAL_BLUEPRINT'] = socials_found

def _send_mail(msg):
    mail = current_app.extensions.get('mail')
    mail.send(msg)

def _conf_storage_peewee(app, settings):
    raise NotImplementedError()

def _conf_session_peewee(app):
    raise NotImplementedError()

def _conf_security_peewee(app):
    raise NotImplementedError()
        
def _conf_admin_peewee(app):
    raise NotImplementedError()
        
def _conf_storage_mongo(app, settings):
    '''Flask-MongoEngine'''
    from shortener_url.backends.mongo import models
    app.config['MONGODB_SETTINGS'] = settings
    models.db.init_app(app)
    app.db = models.db
    app.models = models
    
def _conf_session_mongo(app):
    '''Flask-MongoEngine'''
    
    from flask_mongoengine import MongoEngineSessionInterface
    app.session_interface = MongoEngineSessionInterface(app.db)

def _conf_security_mongo(app):
    '''Flask-Security MongoDB'''
    
    from flask_security import Security, MongoEngineUserDatastore
    from flask_social_blueprint.core import SocialBlueprint
    from shortener_url.backends.mongo import models

    extensions.login.init_app(app)
    extensions.login.login_view = "/login"
    
    security = Security()
    datastore = MongoEngineUserDatastore(app.db, models.User, models.Role)
    security = security.init_app(app, datastore)
    security.send_mail_task(_send_mail)
    
    SocialBlueprint.init_bp(app, models.SocialConnection, url_prefix="/_social")

    #@app.before_first_request
    #def before_first_request():
    #    for m in [models.User, models.Role, models.SocialConnection]:
    #        m.drop_collection()

    @extensions.login.user_loader
    def load_user(user_id):
        return models.User.objects(_id=user_id)
    
def _conf_admin_mongo(app):
    '''Flask-Admin MongoDB'''
    from shortener_url.backends.mongo.admin import init_admin
    init_admin(app=app, url='/short-admin')
    
def _conf_cors(app):
    '''Flask-Cors'''
    from flask_cors import CORS
    CORS(app, 
         send_wildcard=True, 
         methods=["GET"], 
         resources={r"/api/v1/*": {"origins": "*"}})

def _conf_moment(app):
    '''Flask-Moment'''
    from flask_moment import Moment
    Moment(app)

def _conf_assets(app):
    '''Flask-Assets'''
    
    """
    {% assets "common_css" %}
        <link href="{{ ASSET_URL }}" rel="stylesheet" />
    {% endassets %}
    
    {% assets "common_js" %}
        <script type="text/javascript" src="{{ ASSET_URL }}"></script>
    {% endassets %}
    """
    
    from flask_assets import Bundle
    assets = extensions.assets
    #app.debug = True
    assets.init_app(app)
    
    common_css = [
        #"local/bootstrap-3.3.6/css/bootstrap.min.css",
        #"local/bootstrap-3.3.6/css/bootstrap-theme.min.css",
        "local/font-awesome.min.css",
        "local/toastr.min.css",
    ]
    
    common_js = [
        #"local/jquery.min.js",
        #"local/bootstrap-3.3.6/js/bootstrap.min.js",
        "local/humanize.min.js",
        "local/lodash.min.js",
        "local/bootbox.min.js",
        "local/moment.min.js",
        "local/moment-fr.js",
        "local/toastr.min.js",
        "local/jquery.blockUI.min.js"
    ]

    table_css = [
        "local/bootstrap-table.min.css",
    ]    
    table_js = [
        "local/bootstrap-table.min.js",
        "local/bootstrap-table-cookie.min.js",
        "local/bootstrap-table-export.min.js",
        "local/bootstrap-table-filter-control.min.js",
        "local/bootstrap-table-filter.min.js",
        "local/bootstrap-table-flat-json.min.js",
        "local/bootstrap-table-mobile.min.js",
        "local/bootstrap-table-natural-sorting.min.js",
        "local/bootstrap-table-toolbar.min.js",
        "local/bootstrap-table-en-US.min.js",
        "local/bootstrap-table-fr-FR.min.js",
    ]
    
    form_css = [
        "local/awesome-bootstrap-checkbox.min.css",
        "local/daterangepicker.min.css",
        "local/formValidation.min.css",
        "local/chosen.min.css",
    ] + table_css

    form_js = [
        "local/daterangepicker.min.js",
        "local/formValidation.min.js",
        "local/formvalidation-bootstrap.min.js",
        "local/formvalidation-fr_FR.min.js",
        "local/chosen.jquery.min.js",
        "local/mustache.min.js",
        #"local/jquery.sparkline.min.js",
        #"local/dygraph-combined.js",
    ] + table_js

    #TODO: export    
    """
    table_export_js = [
        'bootstrap-table/extensions/export/bootstrap-table-export.min.js',    
        'bootstrap-table/extensions/flat-json/bootstrap-table-flat-json.min.js',
        'bootstrap-table/extensions/toolbar/bootstrap-table-toolbar.js',
        'table-export/tableExport.js',
        'table-export/jquery.base64.js',
        'table-export/html2canvas.js',
        'table-export/jspdf/libs/sprintf.js',
        'table-export/jspdf/jspdf.js',
        'table-export/jspdf/libs/base64.js'
    ]
    """
    
    #274Ko
    """
    assets.register('common_css', 
                    Bundle(*common_css, 
                        filters='cssmin',
                        output='local/common.min.css'))
    """
    assets.register('common_css',
                    *common_css,
                    output='local/common.min.css', 
                    filters='cssmin')
                    
    assets.register('common_js', 
                    Bundle(*common_js,
                        filters='jsmin', 
                        output='local/common.min.js'))
    
    assets.register('form_css', Bundle(*form_css,
                                       filters='cssmin', 
                                       output='local/form.min.css'))
    
    assets.register('form_js', Bundle(*form_js, 
                                      filters='jsmin',
                                      output='local/form.min.js'))

    assets.register('table_css', Bundle(*table_css,
                                       filters='cssmin', 
                                       output='local/table.min.css'))

    assets.register('table_js', Bundle(*table_js,
                                       filters='jsmin', 
                                       output='local/table.min.js'))
    
    with app.app_context():
        assets.cache = True #not app.debug
        assets.manifest = 'cache' if not app.debug else False
        #assets.debug = app.debug #app.debug
        #print(assets._config._defaults)
        #{'url_expire': None, 'versions': 'hash', 'resolver': <flask_assets.FlaskResolver object at 0x0000000004F15C50>, 'load_path': [], 'updater': 'timestamp', 'url_mapping': {}, 'debug': False, 'manifest': 'cache', 'auto_build': True, 'cache': True}
        """
        toutes les options webassets:
            'directory', 'url', 'debug', 'cache', 'updater', 'auto_build',
            'url_expire', 'versions', 'manifest', 'load_path', 'url_mapping'
        peuvent être paramètrés avec ASSETS_xxx en majuscule

        """

def _conf_default_views(app):

    @app.route("/", endpoint="home")
    def index():
        return render_template("shortener_url/index.html")

    @app.route("/profile")
    @login_required
    def profile():
        return render_template('shortener_url/user/profile.html')

    #@app.route("/login")
    #def login():
    #    return render_template("shortener_url/login.html")

    @app.route("/private")
    @login_required
    def private():
        return "PRIVATE"

def _conf_bp(app):
    from shortener_url.views.api import bp as _api
    
    #/api/v1
    app.register_blueprint(_api, url_prefix='/api/v1')

    #/r
    from shortener_url.views.redirect import bp as _redirect
    app.register_blueprint(_redirect, url_prefix='/r')
    
def create_app(config='shortener_url.settings.Prod'):
    
    env_config = config_from_env('SHORTURL_SETTINGS', config)
    
    app = Flask(__name__)
    app.config.from_object(env_config)    

    app.config['LOGGER_NAME'] = 'shortener_url'
    app._logger = _conf_logging(debug=app.debug, prog_name='shortener_url')
    
    if app.config.get("LOGGING_MAIL_ENABLE", False):
        _conf_logging_mail(app)

    _conf_sentry(app)

    _conf_jsonify(app)

    _conf_errors(app)
    
    _conf_compress(app)
    
    _conf_assets(app)

    _conf_babel(app)
    
    _conf_bootstrap(app)
    
    _conf_default_views(app)

    _conf_social(app)
    
    settings, storage = utils.get_db_config(**app.config.get('DB_SETTINGS'))
    
    if storage == "mongo":
        app.config['STORAGE'] = "mongo"
        if 'DEBUG_TB_PANELS' in app.config:
            app.config['DEBUG_TB_PANELS'].append('flask.ext.mongoengine.panels.MongoDebugPanel')
        _conf_storage_mongo(app, settings)
        _conf_admin_mongo(app)
        _conf_security_mongo(app)
        _conf_session_mongo(app)
    elif storage == "sql":
        app.config['STORAGE'] = "sql"
        _conf_storage_peewee(app, settings)
        _conf_admin_peewee(app)
        _conf_security_peewee(app)
        _conf_session_peewee(app)
    
    _conf_bp(app)

    _conf_moment(app)
    
    _conf_mail(app)
    
    _conf_cors(app)
    
    app.wsgi_app = ProxyFix(app.wsgi_app)

    return app
