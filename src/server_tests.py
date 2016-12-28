#!/usr/bin/env python

import os
import server
import tempfile
import unittest

from flask import Flask, current_app

class ShortiesServerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = server.app
        with self.app.app_context():
            server.app.config['TESTING'] = True
            self.context_app = current_app.test_client()
            try:
                server.init_db()
            except:
                pass

    def login(self, username, password):
        return self.context_app.post('/user_login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.context_app.get('/logout', follow_redirects=True)

    def test_login_route(self):
        rv = self.context_app.get('/user_login')
        assert 'Login' in rv.data

    def test_login_logout(self):
        rv = self.login('geoff.golliher', 'forever')
        assert 'No shorties so far' in rv.data
        rv = self.logout()
        rv = self.login('geoff.golliher', 'foreve')
        assert 'Invalid account information.' in rv.data
        rv = self.logout()
        assert 'Login' in rv.data
        assert 'Invalid' not in rv.data

    def test_signup(self):
        # By proxy this also tests the remote_addr check.
        rv = self.context_app.post('/signup', data=dict(
            username='aquaman', email='brokenway@gmail.com', fullname='Aqua Man', password='1234',
                password2='1234'),
            environ_base={'REMOTE_ADDR': '192.168.0.2'},
            follow_redirects=True)
        assert 'No shorties so far' in rv.data

        rv = self.context_app.post('/signup', data=dict(
            username='aquaman', fullname='Aqua Man', email='brokenway@gmail.com', password='1234',
                password2='1234'),
            environ_base={'REMOTE_ADDR': '192.168.0.2'},
            follow_redirects=True)
        assert 'User already exists.' in rv.data

        rv = self.context_app.post('/signup', data=dict(
            username='dude', fullname='Aqua Man', email='brokenway@gmail.com', password='1234',
                password2='1234'),
            environ_base={'REMOTE_ADDR': '192.168.0.2'},
            follow_redirects=True)
        assert 'Username is too short' in rv.data

        rv = self.context_app.post('/signup', data=dict(
            username='282003a9cff7bbadb41fa05748c21775eb61dccd282003a9cff7bbadb41fa05748c21775eb61dccd282003a9cff7bbadb41fa05748c21775eb61dccd',
            fullname='Aqua Man', email='brokenway@gmail.com', password='1234',
                password2='1234'),
            environ_base={'REMOTE_ADDR': '192.168.0.2'},
            follow_redirects=True)
        assert 'Username is too long' in rv.data

        rv = self.context_app.post('/signup', data=dict(
            username='batman', fullname='Bruce Wayne', email='brokenway@gmail,com', password='1234',
                password2='1234'),
            environ_base={'REMOTE_ADDR': '192.168.0.2'},
            follow_redirects=True)
        assert 'Email address is not valid.' in rv.data

        rv = self.context_app.get('/signup',
                environ_base={'REMOTE_ADDR': '99.127.93.10'})
        assert 'Invalid IP' in rv.data


    def test_add_url(self):
        # No login first
        rv = self.context_app.post('/add', data=dict(
            url='http://www.google.com', short_name=''),
            follow_redirects=True)
        assert '401' in rv.data

        # Login for the rest
        self.login('geoff.golliher', 'forever')
        rv = self.context_app.post('/add', data=dict(
            url='http://www.google.com', short_name=''),
            follow_redirects=True)
        assert 'Your shorties:' in rv.data
        assert 'http://www.google.com' in rv.data
        assert 'cvuMLc' in rv.data

        rv = self.context_app.post('/add', data=dict(
            url='http://www.google.com#$@', short_name=''),
            follow_redirects=True)
        assert 'Invalid' in rv.data

        rv = self.context_app.post('/add', data=dict(
            url='www.google.com', short_name=''),
            follow_redirects=True)
        assert 'Invalid' in rv.data

        rv = self.context_app.post('/add', data=dict(
            url='http://www.katch.com', short_name='zingers'),
            follow_redirects=True)
        assert 'www.katch.com' in rv.data
        assert 'zingers' in rv.data

        rv = self.context_app.post('/add', data=dict(
            url='http://www.katch.com', short_name='zingers'),
            follow_redirects=True)
        assert 'www.katch.com' in rv.data
        assert 'Short name already exists.' in rv.data

    def test_redirects(self):
        self.login('geoff.golliher', 'forever')
        self.context_app.post('/add', data=dict(
            url='http://www.slashdot.org', short_name=''),
            follow_redirects=True)
        rv = self.context_app.get('/cvuMLc/')
        self.assertEqual('302 FOUND', rv.status)
        assert 'http://www.slashdot.org' in rv.data

        # Bad hash
        rv = self.context_app.get('/badhash/', follow_redirects=True)
        assert 'cvuMLc' in rv.data

    def test_ip_restrictions(self):
        rv = server.is_private_ip('208.192.68.3')
        self.assertFalse(rv)
        rv = server.is_private_ip('172.16.4.173')
        self.assertTrue(rv)


if __name__ == '__main__':
    unittest.main()
