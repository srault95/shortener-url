
from functools import wraps
from collections import namedtuple

from flask import abort, request, current_app as app
from flask_security import current_user #, login_user
from flask_login import login_user

BasicAuth = namedtuple('BasicAuth', 'username, password')

def _check_apikey_auth(auth=None):
    
    if current_user.is_authenticated:
        return True
    
    auth = auth or request.authorization or BasicAuth(username=None, password=None)
    apikey = None
    
    if not auth or not auth.username:
        apikey = request.args.get('key')
        if not apikey:
            return False
    
    if not apikey and auth and auth.username:
        apikey = auth.username 

    if not apikey:
        return False

    user = app.models.User._find_one(api_key__exact=apikey)

    if user :
        login_user(user)
        return True

    return False

def auth_apikey_required(fn):

    @wraps(fn)
    def decorated(*args, **kwargs):
        
        if current_user.is_authenticated:
            return fn(*args, **kwargs)
        
        if _check_apikey_auth():
            return fn(*args, **kwargs)
        
        #TODO: 401 or 403
        abort(403)

    return decorated

