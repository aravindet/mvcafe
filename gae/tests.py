import json
import unittest
import webapp2

import main

class TestLogin(unittest.TestCase):
    def test_post(self):
        request = webapp2.Request.blank('/login')
        request.method = 'POST'
        request.body = json.dumps({
            'userId': '12345'
        })
        response = webapp2.Response()
        handler = main.Login(request, response)
        handler.post()
        self.assertEqual(response.status_int, 200)
        self.assertTrue(json.loads(response.body)['status'])

class TestLogout(unittest.TestCase):
    def test_post(self):
        request = webapp2.Request.blank('/login')
        request.method = 'POST'
        request.body = json.dumps({
            'userId': '12345'
        })
        response = request.get_response(main.app)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(json.loads(response.body)['status'])
        request = webapp2.Request.blank('/logout')
        request.method = 'POST'
        response = request.get_response(main.app)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(json.loads(response.body)['status'])

if __name__ == '__main__':
    unittest.main()
