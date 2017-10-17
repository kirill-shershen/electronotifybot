# -*- coding: utf-8 -*-
import os

gae = 1 == 1
if gae:
    import json
    json_data = open('config.json').read()
    config = json.loads(json_data)

def get(name, default = ''):
    if gae:
        if config.has_key(name):
            return config[name]
        else:
            return default
    else:
        return os.environ.get(name, default)

token = get('token')
db_url = get('DATABASE_URL')
SQLALCHEMY_DATABASE_URI = db_url
host = get('HOST')
debug = get('debug') == 'True'
heroku_debug = get('heroku_debug') == 'True'
server_debug = get('server_debug')
try:
    port_debug = int(get('port_debug') or 0)
except ValueError:
    port_debug = 0

WEBHOOK_HOST = get('WEBHOOK_HOST')
WEBHOOK_PORT = int(get('PORT', '5000'))
WEBHOOK_LISTEN = 'localhost'

WEBHOOK_URL_BASE = "https://%s"% (WEBHOOK_HOST)
URL = get('MRSKURL')