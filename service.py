import requests
import re
import telebot
import config
from subprocess import Popen, PIPE
import os
import logger
from time import sleep
import signal
import json
import sys

logger = logger.logger()

BASE_DIR = '/home/orangepi/electronotifybot/'

ngrok_url = 'http://127.0.0.1:4040/status'
local_url = 'http://127.0.0.1:8443/ngrok'

bot = telebot.TeleBot(config.service_token, threaded = False) 
PIDFILE = os.path.join(BASE_DIR, 'notify.pid')

def sendmessage(mes):
    logger.info('send messageto telegram')
    bot.send_message(config.service_chat, mes)   

def check_ngrok():
    res = ''
    try:
	logger.info('get request from ngrok')
	r = requests.get(ngrok_url)
	d = re.search('\w*.ngrok.io', r.text)
        res = d.group(0)
	logger.info('ngrok url is %s' % res)
    except:
        sendmessage('ngrok not working')
	exit(1)
    return res

def start_notify():
    try:
        with open(PIDFILE, 'r') as f:
            pid = int(f.read().strip())
    except:
        pid = None
    try:
	proc = '%s >> %s 2>>%s &' % (os.path.join(BASE_DIR, 'notify.py'),os.path.join(BASE_DIR,'notify.out'), os.path.join(BASE_DIR, 'notify.err'))
	if pid:
   	    #kill old proccess
	    logger.info('kill proc %s ' % proc)
	    os.kill(pid, signal.SIGKILL)
    except:
	logger.warn('process not running')
    try:
	#start new
	logger.info('start new proc %s' % proc)
    	#child = Popen(['python', proc], shell=True, stdout=PIPE, stderr=PIPE)
	os.system('python %s' % proc)
	#logger.info('pid: %d' % child.pid)
	#with open(PIDFILE, 'w+') as f:
	#    f.write('%s\n' % str(child.pid))
	sleep(25)
	logger.info('after 5 sleep')
    except Exception as e:
	sendmessage('error starting notify.py: %s' % e)

def check_notify(res = ''):
    while True:
        try:
            logger.info('get request from notify')
	    r = requests.get(local_url)
	    res = r.text
	    logger.info('local url is %s' % res)
	    break
        except Exception as e:
	    logger.error(e)
	    sleep(2)	
	    start_notify()
    return res

def check_config(ngrok, local):
    if ngrok != local:
	config_file = os.path.join(BASE_DIR, 'config.json')
	json_data = open(config_file).read()
        conf = json.loads(json_data)
	conf['WEBHOOK_HOST'] = ngrok
	with open(config_file, 'w') as outfile:
    	    json.dump(conf, outfile)
	logger.info('change local_url to ngrok_url')
	start_notify()
    logger.info('done')

def main():
    logger.info('check settings')
    ngrok = check_ngrok()
    local = check_notify()
    check_config(ngrok, local)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'restart':
	start_notify()
    else:
    	main()

