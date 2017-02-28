# -*- coding: utf-8 -*-

from pprint import pprint
from pathlib import Path

from slugify import slugify
from decouple import config as config_from_env

from flask import current_app

from flask_script import Command, Option, Manager
from flask_script import prompt_bool
from flask_script.commands import Shell, Server
from flask_assets import ManageAssets

from werkzeug.debug import DebuggedApplication

try:
    from gevent.wsgi import WSGIServer
    HAS_GEVENT = True
except ImportError:
    HAS_GEVENT = False
    pass    

from shortener_url import constants
from shortener_url.utils import utcnow
from shortener_url.extensions import _

def _show_config(app=None):

    if not app:
        app = current_app
    print("-------------------------------------------------------")
    pprint(dict(app.config))
    
    print("-------------------------------------------------------")
    print("app.root_path          : ", app.root_path)
    print("app.config.root_path   : ", app.config.root_path)
    print("app.instance_path      : ", app.instance_path)
    print("app.static_folder      : ", app.static_folder)
    print("app.template_folder    : ", app.template_folder)
    print("-------------Extensions--------------------------------")
    extensions = app.extensions.keys()
    for e in extensions:
        print (e)
    print("-------------------------------------------------------")
    

def _show_urls():
    order = 'rule'
    rules = sorted(current_app.url_map.iter_rules(), key=lambda rule: getattr(rule, order))
    for rule in rules:
        methods = ",".join(list(rule.methods))
        #rule.rule = str passé au début de route()
        print("%-30s" % rule.rule, rule.endpoint, methods)

class ShowUrlsCommand(Command):
    """Show all routes"""

    def run(self, **kwargs):
        _show_urls()

class ShowConfigCommand(Command):
    """Show current configuration"""
    
    def run(self, **kwargs):
        _show_config()        

def main(create_app_func=None):
    
    if not create_app_func:
        from shortener_url.wsgi import create_app
        create_app_func = create_app
    
    class ServerWithGevent(Server):
        help = description = 'Runs the Flask development server with Gevent WSGI Server'
    
        def __call__(self, app, host, port, use_debugger, use_reloader,
                   threaded, processes, passthrough_errors, **kwargs):
            
            #print("kwargs : ", kwargs)
            #{'ssl_key': None, 'ssl_crt': None}

            if use_debugger:
                app = DebuggedApplication(app, evalex=True)
    
            server = WSGIServer((host, port), app)
            try:
                print('Listening on http://%s:%s' % (host, port))
                server.serve_forever()
            except KeyboardInterrupt:
                pass
    
    env_config = config_from_env('SHORTURL_SETTINGS', 'shortener_url.settings.Prod')
    
    manager = Manager(create_app_func, 
                      with_default_commands=False)
    
    #TODO: option de config app pour désactiver run counter
    
    manager.add_option('-c', '--config',
                       dest="config",
                       default=env_config)

    manager.add_command("shell", Shell())

    if HAS_GEVENT:
        manager.add_command("server", ServerWithGevent(
                        host = '0.0.0.0',
                        port=8081)
        )
        manager.add_command("debug-server", Server(
                        host = '0.0.0.0',
                        port=8081)
        )
    else:
        manager.add_command("server", Server(
                        host = '0.0.0.0',
                        port=8081)
        )

    manager.add_command("config", ShowConfigCommand())
    manager.add_command("urls", ShowUrlsCommand())
    manager.add_command("assets", ManageAssets())
    
    from flask_security import script
    manager.add_command('auth-create-user', script.CreateUserCommand())
    manager.add_command('auth-create-role', script.CreateRoleCommand())
    manager.add_command('auth-add-role', script.AddRoleCommand())
    manager.add_command('auth-remove-role', script.RemoveRoleCommand())
    manager.add_command('auth-activate-user', script.ActivateUserCommand())
    manager.add_command('auth-deactivate-user', script.DeactivateUserCommand())
    
    manager.run()

if __name__ == "__main__":
    # python -m shortener_url.manager assets build
    # python -m shortener_url.manager server -p 8081 -R
    main()

