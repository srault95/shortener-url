# -*- coding: utf-8 -*-

from copy import deepcopy
from jinja2 import Markup
import wtforms as wtf
from wtforms import fields

from flask_admin.form import rules
from flask import abort, redirect, url_for, request, session, current_app, flash
from flask_admin.contrib.mongoengine import ModelView as BaseModelView
from flask_admin import AdminIndexView as BaseAdminIndexView
from flask_admin import helpers, expose
from flask_admin import Admin
from flask_admin.contrib.mongoengine import filters
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_admin.actions import action

from flask_babelex import format_date, format_datetime, format_number

from flask_security import current_user, login_required, roles_required, roles_accepted

import pycountry

from shortener_url.extensions import gettext, lazy_gettext
from shortener_url import constants
from . import models

class TextReadOnlyWidget(wtf.widgets.TextInput):
    
    def __call__(self, field, **kwargs):
        kwargs["readonly"] = "true"
        return wtf.widgets.TextInput.__call__(self, field, **kwargs)

class ReadOnlyStringField(wtf.StringField):
    widget = TextReadOnlyWidget()

class SecureView(object):

    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        if not current_user.is_authenticated:
            return abort(401)
        return abort(403)

class ModelView(SecureView, BaseModelView):

    form_overrides = dict(
        internal_field=wtf.HiddenField,
        mark_for_delete=wtf.HiddenField,
    )
    
    column_details_exclude_list = [
        '_cls', 
        'id', 
        'internal_field', 
        'mark_for_delete'
    ]

    action_disallowed_list = ['untrash', 'delete'] #'trash', 

    #details_template = 'shortener_url/admin/model/details.html'
    
    page_size = 10
    #details_modal = True
    can_view_details = True
    can_export = True

    _edit_form_readonly_fields = []
    
    def edit_form(self, obj=None):
        ''''Pour mettre des champs en Read Only'''        
        from flask_admin.helpers import get_form_data
        self._edit_form_class = self.get_edit_form()
        form_class = deepcopy(self._edit_form_class)
        for field in self._edit_form_readonly_fields:
            setattr(form_class, field, ReadOnlyStringField())
        return form_class(get_form_data(), obj=obj)
    
    @action('trash',
            lazy_gettext('Push to trash'),
            lazy_gettext('Are you sure ?'))
    def action_trash(self, ids):
        qs = self.model.objects(pk__in=ids)
        count = qs.update(set__mark_for_delete=1, multi=True)
        if count:
            flash(gettext("%(count)s records has been push to trash.", count=count))

    @action('untrash',
            lazy_gettext('Restore from trash'),
            lazy_gettext('Are you sure ?'))
    def action_untrash(self, ids):
        qs = self.model.objects(pk__in=ids)
        count = qs.update(set__mark_for_delete=0, multi=True)
        if count:
            flash(gettext("%(count)s records has been restore from trash.", count=count))
    
    def get_query(self):
        return self.model.objects(mark_for_delete__ne=1)

    def get_details_columns(self):
        columns = [field for field in self.model._fields_ordered]

        return self.get_column_names(
            only_columns=columns,
            excluded_columns=self.column_details_exclude_list,
        )
        
#---Admin Views

class URLView(ModelView):
    
    column_searchable_list = ('author', 'origin', 'target')
    
    column_list = ('author', 'origin', 'target', 'created', 'updated', 'last_verified')

    form_overrides = dict(internal_field=wtf.HiddenField,
                          mark_for_delete=wtf.HiddenField)

class UserView(ModelView):
    _name = gettext(u"Users")
    
    column_list = ('email',)

    #column_searchable_list = ('email',)

class RoleView(ModelView):
    _name = gettext(u"Rules")
    
class SocialConnectionView(ModelView):
    _name = gettext(u"Social Connections")

class AdminIndexView(BaseAdminIndexView):
    
    @expose('/')
    def index(self):
        #self._template_args['rooms'] = []
        return super().index()

def init_admin(app, 
               admin_app=None, 
               url='/admin',
               name="Shortener URL Admin",
               base_template='shortener_url/admin/layout.html',
               #index_template='shortener_url/admin/index.html',
               index_view=None,
               ):

    index_view = index_view or AdminIndexView(
                                              #template=index_template, 
                                              url=url,
                                              name="home")
    
    admin = admin_app or Admin(app,
                               url=url,
                               name=name,
                               index_view=index_view, 
                               base_template=base_template, 
                               template_mode='bootstrap3')

    admin.add_view(URLView(models.URL, 
                           name=gettext("URLs")))

    admin.add_view(UserView(models.Role, 
                            #name=gettext("Roles"),
                            category=gettext("Users")))
        
    admin.add_view(UserView(models.User, 
                            #name=gettext("Users"),
                            category=gettext("Users")))

    admin.add_view(UserView(models.SocialConnection, 
                            #name=gettext("Social Connections"),
                            category=gettext("Users")))
