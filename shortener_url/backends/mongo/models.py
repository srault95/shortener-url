# -*- coding: utf-8 -*-

import logging
import hashlib

from mongoengine import DENY
from mongoengine.queryset.visitor import Q
from mongoengine import Document
from mongoengine import fields

from flask_security import UserMixin, RoleMixin

from shortener_url import constants
from shortener_url.extensions import gettext
from shortener_url import utils
from shortener_url.countries import COUNTRIES_CHOICES
from shortener_url.url import encode_url

logger = logging.getLogger(__name__)

from flask_mongoengine import MongoEngine
db = MongoEngine()

class BaseDocument(db.Document):

    #ex: demo values
    internal_field = fields.IntField(default=0)
    
    #trash
    mark_for_delete = fields.IntField(default=0)

    active = fields.BooleanField(default=True)

    created = fields.DateTimeField(default=utils.utcnow)

    updated = fields.DateTimeField()

    @classmethod
    def _count(cls, **kwargs):
        return cls.objects(**kwargs).count()

    @classmethod
    def _find(cls, **kwargs):
        return cls.objects(**kwargs)

    @classmethod
    def _find_one(cls, **kwargs):
        print("!!find one : ", kwargs)
        return cls._find(**kwargs).first()

    @classmethod
    def _create(cls, **kwargs):
        return cls(**kwargs).save()

    @classmethod
    def _update(cls, doc=None, **kwargs):
        return doc.update(**kwargs)
        #return doc

    @classmethod
    def _delete(cls, doc=None):
        return doc.delete()
    
    def get_pk(self):
        return self.pk()
    
    def as_dict(self):
        return self.to_mongo().to_dict()    
    
    def as_json(self):
        return self.to_json()
    
    def save(self, **kwargs):
        if self.pk:
            self.last_updated = utils.utcnow()
        return db.Document.save(self, **kwargs)
    
    meta = {
        'abstract': True,
    }
    
class Role(BaseDocument, RoleMixin):
    
    name = fields.StringField(required=True, unique=True, max_length=80)
    
    description = fields.StringField(max_length=255)

    def __unicode__(self):
        return self.name

    meta = {
        'collection': 'role',
        'indexes': ['name'],
    }
    

class User(BaseDocument, UserMixin):

    email = fields.StringField(required=False, unique=True, max_length=200) 
    #username = fields.StringField(required=False, unique=True, max_length=200)
    
    password = fields.StringField(max_length=200)

    #TODO: last_ip, last_login
    
    api_key = fields.StringField(max_length=255)
    
    locale = fields.StringField()

    confirmed_at = fields.DateTimeField()
    
    remember_token = fields.StringField(max_length=255)
    
    authentication_token = fields.StringField(max_length=255)
    
    first_name = fields.StringField(max_length=120)
    
    last_name = fields.StringField(max_length=120)
    
    roles = fields.ListField(fields.ReferenceField(Role, reverse_delete_rule=DENY), default=[])

    @property
    def username(self):
        return self.email  
    
    @property
    def is_active(self):
        return self.active  

    @property
    def cn(self):
        if not self.first_name or not self.last_name:
            return self.email
        return u"{} {}".format(self.first_name, self.last_name)

    @property
    def id(self):
        return self.pk

    @classmethod
    def by_email(cls, email):
        return cls.objects(email=email).first()

    @property
    def gravatar(self):
        email = self.email.strip()
        encoded = hashlib.md5(email.encode("utf-8")).hexdigest()
        return "https://secure.gravatar.com/avatar/%s.png" % encoded

    def social_connections(self):
        return SocialConnection.objects(user=self)

    def __unicode__(self):
        return self.email

    meta = {
        'collection': 'user',
        'indexes': ['email', 'api_key'], #TODO: dans les 2 sens pour query optimisé
    }

class SocialConnection(BaseDocument):
    
    user = fields.ReferenceField(User)
    
    provider = fields.StringField(max_length=255)
    
    profile_id = fields.StringField(max_length=255)
    
    username = fields.StringField(max_length=255)
    
    email = fields.StringField(max_length=255)
    
    access_token = fields.StringField(max_length=255)
    
    secret = fields.StringField(max_length=255)
    
    first_name = fields.StringField(max_length=255, help_text=gettext("First Name"))
    
    last_name = fields.StringField(max_length=255, help_text=gettext("Last Name"))
    
    cn = fields.StringField(max_length=255, help_text=gettext("Common Name"))
    
    profile_url = fields.StringField(max_length=512)
    
    image_url = fields.StringField(max_length=512)

    def get_user(self):
        return self.user

    @classmethod
    def by_profile(cls, profile):
        provider = profile.data["provider"]
        return cls.objects(provider=provider, profile_id=profile.id).first()

    @classmethod
    def from_profile(cls, user, profile):
        if not user or user.is_anonymous:
            email = profile.data.get("email")
            if not email:
                msg = "Cannot create new user, authentication provider did not not provide email"
                logging.warning(msg)
                raise Exception(_(msg))
            conflict = User.objects(email=email).first()
            if conflict:
                msg = "Cannot create new user, email {} is already used. Login and then connect external profile."
                msg = _(msg).format(email)
                logging.warning(msg)
                raise Exception(msg)

            now = utils.utcnow()
            user = User(
                email=email,
                first_name=profile.data.get("first_name"),
                last_name=profile.data.get("last_name"),
                confirmed_at=now,
                active=True,
            )
            user.save()

        connection = cls(user=user, **profile.data)
        connection.save()
        return connection

    def __unicode__(self):
        return self.email

    meta = {
        'collection': 'socialconnection',
        'indexes': ['user', 'profile_id'],
    }

class URL(BaseDocument):
    """Store All Urls"""

    #User.email - no direct reference
    author = fields.EmailField(required=True) 

    #Original URL before convert
    origin = fields.StringField(required=True, unique=True)
    
    #TODO: ip_address author ? 

    #Convert URL
    target = fields.StringField(required=True, unique=True) 
    
    #status = fields.IntField(choices=constants.STATUS,
    #                         default=constants.STATUS_DRAFT, 
    #                         required=True)
    
    #Original url Verified by robot
    last_verified = fields.DateTimeField()
    
    def save(self, **kwargs):
        self.target = encode_url(self.origin)
        return super().save(**kwargs)

    def __unicode__(self):
        return self.origin

    meta = {
        'collection': 'url',
        'indexes': ['origin', 'target'], #TODO: dans les 2 sens pour query optimisé
    }

class URLStat(db.Document):
    """Statistic for redirect usage"""
    
    #User.email - no direct reference
    author = fields.EmailField(required=True) 

    #URL.target - no direct reference
    target = fields.StringField(required=True)
    
    date = fields.DateTimeField(default=utils.utcnow)
    
    count = fields.LongField(default=0, required=True)
    
    #Json Text ?
    useragent = fields.StringField()
     
    def __unicode__(self):
        return "%s - %s" % (self.author, self.target)



