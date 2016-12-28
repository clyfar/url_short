#!/usr/bin/env python
# Author: Geoffrey Golliher (ggolliher@katch.com)

import hashlib
import os
import re

from database import database
from datadog import ThreadStats
from datadog import initialize
from flask import Flask, request, session, g, redirect, abort, render_template
from functools import wraps
from hash_lib import HashBuilder
from validate_email import validate_email
from werkzeug.routing import BaseConverter

options = {
    'api_key':'59b079536c746acf32583e049265791e',
    'app_key':'9cd55dfd35599735baf57f3e43078fa62bd9bed7'
}

initialize(**options)

app = Flask(__name__)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='ou812',
    # DB_TYPE='postgres',
    # DB_HOST='localhost'
    # For testing and local development. Testing will work if you have a
    # local postgres database running and initialized.
    DB_TYPE='sqlite',
    DB_HOST=os.path.join(app.root_path, 'shorty.db')
))

datab = database.Database(app.config['DB_TYPE'], app).pickAndReturn(
        app.config['DB_HOST'])

app.config.update(dict(DATABASE=datab))

stats = ThreadStats()
stats.start()


def record_call(fn):
    """Simple wrapper to record each function call throughout the stack."""
    @wraps(fn)
    def call(*args, **kwargs):
        stats.increment('test.shorties.{0}.calls'.format(fn.__name__))
        return fn(*args, **kwargs)
    return call


@record_call
def is_private_ip(uip):
    is_private = re.compile(
        r"(127\.0\.0\.1)|(10\.)|(172\.(1[6-9]|2[0-9]|3[0-1])\.)|(192\.168\.)")
    return is_private.search(uip)

@record_call
def get_shorties():
    stats.increment('test.shorties.get_shorties.hits')
    db = get_db().cursor()
    db.execute(
        "select id, url, key, owner from shorties " +
        "where owner = '{}' order by id".format(session.get('username')))
    shorties = db.fetchall()
    shorties = app.config['DATABASE'].transform_shorties(shorties)
    return shorties


@record_call
def connect_db():
    """Connects to the specific database."""
    g.db = app.config['DB_TYPE']
    return app.config['DATABASE'].connect_db()


@record_call
def init_db():
    """Initializes the database."""
    app.config['DATABASE'].init_db(app)


@app.cli.command('initdb')
@record_call
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


@record_call
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    stats.increment('test.shorties.db_connect.request')
    if not hasattr(g, 'db'):
        g.db = connect_db()
        stats.increment('test.shorties.db_connect.connect')
    return g.db


@app.teardown_appcontext
@record_call
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/shorties')
@record_call
def show_shorties():
    if not session.get('logged_in'):
        return redirect('/user_login')
    shorties = get_shorties()
    return render_template('show_shorties.html', shorties=shorties)


@app.route('/signup', methods=['GET', 'POST'])
@record_call
def signup():
    uip = request.remote_addr
    if not is_private_ip(uip):
        return render_template('forbidden.html', error="Invalid IP")
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        username = request.form['username']
        password = hashlib.sha1(request.form['password'].strip()).hexdigest()
        if not validate_email(email):
            error = 'Email address is not valid.'
            return render_template('signup.html', error=error)
        verified = 1
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "select count(username) from users where username = '{}';".format(
                username))
        try:
            uname = cur.fetchall()[0][0]
            # Have noticed inconsistent cursor behavior.
            # Sometimes there is no index and an exception is raised.
            # Sometimes the index has a value of 0 which doesn't raise.
            # Checking and raising here.
            if not uname:
                raise Exception
            error = "User already exists."
            return render_template('signup.html', error=error)
        except:
            if len(username) > 64:
                error = "Username is too long it must be less than 64 characters and more than 5 characters."
                return render_template('signup.html', error=error)
            if len(username) < 5:
                error = "Username is too short it must be less than 64 characters and more than 5 characters."
                return render_template('signup.html', error=error)
            cur.execute(
                "insert into users (fullname, email, username, password, verified) " +
                "values ('{}','{}','{}', '{}', {});".format(
                    fullname, email, username, password, verified))
            db.commit()
            session['logged_in'] = True
            session['username'] = username
            return redirect('/shorties')
    else:
        return render_template('signup.html')


@app.route('/add', methods=['POST'])
@record_call
def add_entry():
    """
        This is really awful code. I should split this into several different methods.
        I was rushing myself.
    """
    if not session.get('logged_in'):
        abort(401)
    error = None
    db = get_db()
    cur = db.cursor()
    shorties = get_shorties()

    # Internal addresses only.
    # TODO(geoffrey): Break this out into another method.
    is_valid = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    extra_query = ''
    if app.config['DB_TYPE'] == 'postgres':
        extra_query = 'RETURNING id'
    try:
        is_valid.match(request.form['url']).groups()
    except AttributeError as e:
        error = "Invalid URL"
        return render_template(
            '/show_shorties.html',
            shorties=shorties, error=error)
    db = get_db()
    cur = db.cursor()
    owner = session['username']
    sname = None
    error = None
    # TODO(geoffrey): Break this out into another method.
    if request.form['short_name']:
        try:
            cur.execute("select key from shorties where key = '{}';".format(request.form['short_name']))
            sname = cur.fetchall()[0][0]
            error = 'Short name already exists.'
            return render_template(
                '/show_shorties.html',
                shorties=shorties, error=error)
        except:
            sname = request.form['short_name']
    cur.execute(
        "insert into shorties (url, owner) values ('{}', '{}') {} ;".format(
            request.form['url'], owner, extra_query))
    i = app.config['DATABASE'].last_id(cur)
    if not request.form['short_name']:
        hash_builder = HashBuilder(32)
        url_hash = hash_builder.build_hash(i)
    else:
        url_hash = request.form['short_name']
    sha1 = hashlib.sha1(request.form['url']).hexdigest()
    cur.execute(
        "update shorties set key='{}', url_hash='{}' where id='{}';".format(
            url_hash, sha1, i))
    db.commit()
    shorties = get_shorties()
    return render_template(
        '/show_shorties.html',
        shorties=shorties, error=error)


@app.route('/user_login', methods=['GET', 'POST'])
@record_call
def login():
    error = None
    if request.method == 'POST':
        uname = None
        username = request.form['username']
        password = hashlib.sha1(request.form['password'].strip()).hexdigest()
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT username FROM users WHERE password = '{}' and username = '{}'".format(
            password, username))
        try:
            uname = cur.fetchall()[0][0]
        except IndexError:
            error = "Invalid account information. {}".format(uname)
        if uname == username:
            session['logged_in'] = True
            session['username'] = username
            return redirect('/shorties')
        else:
            error = "Invalid account information. {}".format(uname)
    return render_template('login.html', error=error)


# This regex will catch all paths that haven't been explicitly defined
# and match the regex.
@app.route('/<regex("[a-zA-Z0-9-_]{3,64}.*"):path>/', methods=['GET'])
@record_call
def redirect_shortie(path):
    after_hash = None
    reg = "http://%s/([a-zA-Z0-9-_]{3,64})(.*)" % request.host
    matcher = re.compile(reg)
    if path.find('/') is not -1:
        m = matcher.match(request.url)
        after_hash = m.group(2)
        path = m.group(1)
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "select url from shorties where key = '{}';".format(path))
    try:
        short = cur.fetchall()[0][0]
        if after_hash:
            short = "{}{}".format(short, after_hash)
        return redirect(short, code=302)
    except IndexError as e:
        shorties = get_shorties()
        error = "Invalid Hash"
        return render_template(
            '/show_shorties.html',
            shorties=shorties, error=error)


@app.route('/logout')
@record_call
def logout():
    session.pop('logged_in', None)
    return redirect('/shorties')

@app.route('/reset-password', methods=('GET', 'POST',))
def forgot_password():
    # TODO(geoffrey): Finish this. Can use hash_lib to generate an expiring token.
    error = None
    token = request.args.get('token', None)
    return render_template('reset.html', error=error)


@app.route('/')
@record_call
def root():
    return redirect('/shorties')
