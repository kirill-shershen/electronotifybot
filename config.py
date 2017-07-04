# -*- coding: utf-8 -*-
import os

gae = os.environ.get('USER') == 'vol1001_01'
if gae:
    from google.appengine.ext import ndb
    class Settings(ndb.Model):
        name = ndb.StringProperty()
        value = ndb.StringProperty()

def get(name, default = ''):
    if gae:
        val = Settings.query(Settings.name == name).get()
        if not val.value:
            val.value = default
        return val.value
    else:
        return os.environ.get(name, default)

token = get('token')
db_url = get('DATABASE_URL')
SQLALCHEMY_DATABASE_URI = db_url
host = get('host')
debug = get('debug') == 'True'
heroku_debug = get('heroku_debug') == 'True'
server_debug = get('server_debug')
try:
    port_debug = int(get('port_debug') or 0)
except ValueError:
    port_debug = 0

WEBHOOK_HOST = get('WEBHOOK_HOST')
WEBHOOK_URL_PATH = '/bot'
WEBHOOK_PORT = int(get('PORT', '5000'))
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_URL_BASE = "https://%s/%s"% (WEBHOOK_HOST,WEBHOOK_URL_PATH)