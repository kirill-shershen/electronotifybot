# -*- coding: utf-8 -*-
import os


debug = os.environ.get('debug') == 'True'
token = os.environ.get('token')
db_url = os.environ.get('DATABASE_URL')

WEBHOOK_HOST = 'electronotifybot.herokuapp.com'
WEBHOOK_URL_PATH = '/bot'
WEBHOOK_PORT = os.environ.get('PORT',5000)
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_URL_BASE = "https://%s/%s"% (WEBHOOK_HOST,WEBHOOK_URL_PATH)


