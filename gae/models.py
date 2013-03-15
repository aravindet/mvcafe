from google.appengine.ext import ndb
from webapp2_extras.appengine.auth.models import User

ORDER_QUEUED = 2
ORDER_STARTED = 1
ORDER_DONE = 0
ORDER_CANCELLED = -1

class User(User):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

class Coffee(ndb.Model):
    coffee_type = ndb.StringProperty()
    eta = ndb.IntegerProperty()

    @classmethod
    def get_type(cls, coffee_type):
        return cls.query(cls.coffee_type==coffee_type).get()

class Order(ndb.Model):
    coffee = ndb.KeyProperty(kind=Coffee)
    user = ndb.KeyProperty(kind=User)
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    started = ndb.DateTimeProperty()
    status = ndb.IntegerProperty(default=ORDER_QUEUED)

    @classmethod
    def queued(cls):
        return cls.query(cls.status>0).fetch()

    @classmethod
    def brewing(cls):
        return cls.query(cls.status==1).fetch()

    @classmethod
    def done(cls):
        return cls.query(cls.status==0).fetch()

    @classmethod
    def cancelled(cls):
        return cls.query(cls.status==-1).fetch()
