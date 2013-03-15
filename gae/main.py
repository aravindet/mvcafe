import json
import datetime
import time
import logging
import webapp2
import jinja2
import os
from webapp2_extras import sessions, auth

import config
from models import User, Coffee, Order, ORDER_QUEUED, ORDER_DONE, ORDER_STARTED, ORDER_CANCELLED

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

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
    def user(self):
        user_id = self.session.get('user_id')
        if not user_id:
            return None
        user = User.get_by_id(user_id)
        return user

    def json_data(self):
        return self.request.POST

class Login(BaseHandler):
    def post(self):
        json_data = self.json_data()
        user_id = self.session.get('user_id') or json_data['id']
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
        user = self.user
        if not user:
            self.abort(401)
        json_data = self.json_data()
        coffee_type = json_data['type']
        coffee = Coffee.get_type(coffee_type)
        if not coffee:
            self.response.status_int = 404
            self.response.out.write(json.dumps({
                'status': False,
                'message': 'Coffee with type %s not found.' % coffee_type
            }))
            return
        order = Order(
            user=user.key,
            coffee=coffee.key,
        )
        order.put()
        self.response.content_type = 'application/json'
        self.response.out.write(json.dumps({
            'status': True
        }))

class StartOrder(BaseHandler):
    def post(self, order_id):
        user = self.user
        if not user:
            self.abort(401)
        # TODO: only allow Sharon
        order = Order.get_by_id(str(order_id))
        if not order or order.status != ORDER_QUEUED:
            self.response.status_int = 404
            self.response.out.write(json.dumps({
                'status': False,
                'message': 'Can\'t find that order.'
            }))
            return
        order.status = ORDER_STARTED
        order.started = datetime.datetime.now()
        order.put()
        self.response.content_type = 'application/json'
        self.response.out.write(json.dumps({
            'status': True
        }))

class FinishOrder(BaseHandler):
    def post(self, order_id):
        user = self.user
        if not user:
            self.abort(401)
        # TODO: only allow Sharon
        order = Order.get_by_id(str(order_id))
        if not order or order.status != ORDER_STARTED:
            self.response.status_int = 404
            self.response.out.write(json.dumps({
                'status': False,
                'message': 'Can\'t find that order.'
            }))
            return
        order.status = ORDER_DONE
        order.finished = datetime.datetime.now()
        order.put()
        self.response.content_type = 'application/json'
        self.response.out.write(json.dumps({
            'status': True
        }))

class CancelOrder(BaseHandler):
    def post(self, order_id):
        user = self.user
        if not user:
            self.abort(401)
        # TODO: only allow Sharon
        order = Order.get_by_id(str(order_id))
        if not order or order.status != ORDER_QUEUED:
            self.response.status_int = 404
            self.response.out.write(json.dumps({
                'status': False,
                'message': 'Can\'t find that order.'
            }))
            return
        if order.user.key != user.key:
            self.response.status_int = 403
            self.response.out.write(json.dumps({
                'status': False,
                'message': 'Not your order.'
            }))
            return
        order.status = ORDER_CANCELLED
        order.put()
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
                'userId': o.user.string_id(),
                'orderedAt': time.mktime(o.created.utctimetuple()),
                'startedAt': time.mktime(o.started.utctimetuple()) if o.started else None,
                'finishedAt': time.mktime(o.finished.utctimetuple()) if o.finished else None
            } for o in queued
        ]
        users = User.query()
        users = [
            {'id': u.key.string_id(),
             'name': '',
             'photo': ''}
            for u in users
        ]
        self.response.content_type = 'application/json'
        self.response.out.write(json.dumps({
            'time': timestamp,
            'orders': orders,
            'users': users
        }))

class Home(BaseHandler):
    def get(self):
        user = self.user
        context = {
            'user': user
        }
        template = jinja_env.get_template('index.html')
        self.response.write(template.render(context))

class CreateCoffee(BaseHandler):
    def get(self):
        coffee_type = self.request.get('type')
        coffee = Coffee.query(Coffee.coffee_type == coffee_type).get()
        if coffee:
            return
        coffee = Coffee(
            coffee_type=coffee_type,
            eta=3*60)
        coffee.put()

app = webapp2.WSGIApplication([
    ('/login/?', Login),
    ('/logout/?', Logout),
    ('/orders/?', PlaceOrder),
    ('/orders/(.*)/start/?', StartOrder),
    ('/orders/(.*)/ready/?', FinishOrder),
    ('/orders/(.*)/cancel/?', CancelOrder),
    ('/status/?', OrderStatus),
    ('/home/?', Home),
    ('/create_coffee/?', CreateCoffee),
], config={
    'webapp2_extras.sessions': config.webapp2_sessions,
    'webapp2_extras.auth': config.webapp2_auth
},
    debug=True)

