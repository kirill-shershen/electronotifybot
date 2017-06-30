# -*- coding: utf-8 -*-
import os


token = os.environ.get('token')
db_url = os.environ.get('DATABASE_URL')
SQLALCHEMY_DATABASE_URI = db_url
host = os.environ.get('host')
debug = os.environ.get('debug') == 'True'
heroku_debug = os.environ.get('heroku_debug') == 'True'
server_debug = os.environ.get('server_debug')
try:
    port_debug = int(os.environ.get('port_debug') or 0)
except ValueError:
    port_debug = 0

WEBHOOK_HOST = 'electronotifybot.herokuapp.com'
WEBHOOK_URL_PATH = '/bot'
WEBHOOK_PORT = os.environ.get('PORT',5000)
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_URL_BASE = "https://%s/%s"% (WEBHOOK_HOST,WEBHOOK_URL_PATH)