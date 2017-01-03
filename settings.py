# -*- coding: utf-8 -*-
import os
import logging
import sys


debug = os.environ.get('debug') == 'True'
token = os.environ.get('token')
db_url = os.environ.get('DATABASE_URL')

WEBHOOK_HOST = 'electronotifybot.herokuapp.com'
WEBHOOK_URL_PATH = '/bot'
WEBHOOK_PORT = os.environ.get('PORT',5000)
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_URL_BASE = "https://%s/%s"% (WEBHOOK_HOST,WEBHOOK_URL_PATH)

def logger():
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        # set up logging to console
        console1 = logging.StreamHandler(sys.stdout)
        # console1.setLevel(logging.DEBUG)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(asctime)-15s %(levelname)s:%(filename)s:%(lineno)d -- %(message)s')
        console1.setFormatter(formatter)

        logger.addHandler(console1)
        logger.setLevel(logging.DEBUG)
    return logger
