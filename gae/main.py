import json
import datetime
import time
import logging
import webapp2
from webapp2_extras import sessions, auth

import config
from models import User, Coffee, Order

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save # all # sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns # a # session # using # the # default # cookie # key.
        return self.session_store.get_session()

    @webapp2.cached_property
    def auth(self):
        return auth.get_auth(request=self.request)

    @webapp2.cached_property
    def user(self):
        user = self.auth.get_user_by_session()
        return user

    @webapp2.cached_property
    def user_model(self):
        user_model, timestamp = self.auth.store.user_model.get_by_auth_token(
            self.user['user_id'],
            self.user['token']) if self.user else (None, None)
        return user_model

    def json_data(self):
        return json.loads(self.request.body)

class Login(BaseHandler):
    def post(self):
        json_data = self.json_data()
        user_id = self.session.get('user_id') or json_data['userId']
        self.session['user_id'] = user_id
        user = User.get_or_insert(user_id, auth_ids=['facebook:' + user_id])
        user.put()
        self.response.content_type = 'application/json'
        self.response.out.write(json.dumps({
            'status': True
        }))

class Logout(BaseHandler):
    def post(self):
        self.session.pop('user_id')
        self.response.content_type = 'application/json'
        self.response.out.write(json.dumps({
            'status': True
        }))

class PlaceOrder(BaseHandler):
    def post(self):
        user_id = self.session.get('user_id')
        if not user_id:
            self.abort(401)
        user = User.get_by_id(user_id)
        if not user:
            self.abort(401)
        json_data = self.json_data()
        coffee_type = json_data['type']
        coffee = Coffee.get_type(coffee_type)
        if not coffee:
            self.abort(404)
        order = Order(
            user=user.key,
            coffee=coffee.key,
        )
        self.response.content_type = 'application/json'
        self.response.out.write(json.dumps({
            'status': True
        }))

class OrderStatus(BaseHandler):
    def get(self):
        queued = Order.queued()
        timestamp = time.mktime(datetime.datetime.now().utctimetuple())
        orders = [
            {
                'id': o.key.id(),
                'type': o.coffee.get().coffee_type,
                'userId': o.user.key.string_id(),
                'orderedAt': time.mktime(o.created.utctimetuple()),
                'startedAt': time.mktime(o.started.utctimetuple()) if o.started else None,
                'finishedAt': time.mktime(o.finished.utctimetuple()) if o.finished else None
            } for o in queued
        ]
        self.response.content_type = 'application/json'
        self.response.out.write(json.dumps({
            'time': timestamp,
            'orders': orders
        }))

app = webapp2.WSGIApplication([
    ('/login/?', Login),
    ('/logout/?', Logout),
    ('/orders/?', PlaceOrder),
    ('/status/?', OrderStatus),
], config={
    'webapp2_extras.sessions': config.webapp2_sessions,
    'webapp2_extras.auth': config.webapp2_auth
},
    debug=True)

