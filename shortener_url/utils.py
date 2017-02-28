
import arrow
from urllib.parse import urlparse

def utcnow():
    return arrow.utcnow().datetime

def get_db_config(**db_settings):
    
    host = db_settings.get('host', None) 
    options = db_settings.get('options', {})
    
    if not host:
        raise Exception("not host found in settings")

    url = urlparse(host)
    
    if url.scheme in ['sqlite', 'postgres', 'mysql']:
        settings = {
            'db_name': host,
            'db_options': options
        }
        if not 'threadlocals' in options:
            if url.scheme == 'sqlite':
                settings['db_options']['threadlocals'] = True
        else:
            if not url.scheme == 'sqlite':
                settings['db_options'].pop('threadlocals')
    
        return settings, 'sql'
    
    elif url.scheme == 'mongodb':
        settings = {
            'host': host,
            'db': options.get('db')
            #'tz_aware': True,
        }
        return settings, 'mongo'
    else:
        raise Exception("not valid scheme in db configuration")

