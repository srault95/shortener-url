from flask_cache import Cache
from flask_mail import Mail
from flask_assets import Environment
from flask_login import LoginManager

assets = Environment()

cache = Cache()

mail = Mail()

login = LoginManager()

try:
    from flask_babel import Babel, lazy_gettext, gettext
    babel = Babel()
    _ = gettext
except Exception as err:
    print("ERROR BABEL !!! : ", str(err))
    gettext = lambda s, **kwargs: s
    _ = gettext
    lazy_gettext = gettext 
    class Babel(object):
        def __init__(self, *args, **kwargs):
            pass
        def init_app(self, app):
            pass
    babel = Babel()


