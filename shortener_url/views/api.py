# -*- coding: utf-8 -*-

from flask import request, Blueprint, abort, current_app as app
from flask_security import current_user

from shortener_url import json_tools
from shortener_url.decorators import auth_apikey_required

bp = Blueprint('api', __name__)

#TODO: Limit decorator
#TODO: test accept json
@bp.route('/create', endpoint="create", methods=('POST',))
@auth_apikey_required
def create_url():
    
    url = request.args.get('url')
    
    if not url:
        return abort("url parameter is required")
    
    try:
        #TODO: author !
        print("current_user.email : ", current_user.email)
        doc = app.models.URL._create(author=current_user.email, 
                                     origin=url)
        return json_tools.json_simple_response(doc.target)
    except Exception as err:
        #TODO: exist error
        print("ERROR : ", str(err))
        
    abort(401)


