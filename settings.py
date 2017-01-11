# -*- coding: utf-8 -*-
import os
import logging
import sys


debug = os.environ.get('debug') == 'True'
heroku_debug = os.environ.get('heroku_debug') == 'True'
token = os.environ.get('token')
db_url = os.environ.get('DATABASE_URL')
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

def logger():
    if heroku_debug == True:
        lvl = logging.DEBUG
    else:
        lvl = logging.INFO
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        # set up logging to console
        console1 = logging.StreamHandler(sys.stdout)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(asctime)-15s %(levelname)s:%(filename)s:%(lineno)d -- %(message)s')
        console1.setFormatter(formatter)

        logger.addHandler(console1)
        logger.setLevel(lvl)
    return logger
