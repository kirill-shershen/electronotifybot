# -*- coding: utf-8 -*-

import logger
from datetime import datetime
import telebot
import user as u
import config
from models import db, UserNotify as un, ElectroOutage as eo

logger = logger.logger()

class Scheduler():

    def __init__(self):
        self.events = {}
        self.bot = telebot.TeleBot(config.token)
        self.prepare()

    def prepare(self):
        #usernotify = u.get_notify()
	#usernotify = u.NotifyList()
	#usernotify.load()
        #outage = u.get_useroutage()
	#outage = u.OutageList()
	#outage.load_all()
	outage = db.session().query(eo.City, eo.Street, eo.Date, eo.StrDate, eo.Reason, un.User_ID, un.Notify).join((un, un.ID == eo.UserNotify_ID)).all()
        date = datetime.now().replace(minute=0, hour=0, second=0, microsecond=0)
        for row in outage:
            if abs((date - row.Date).days) == row.Notify:
                self.send(row.User_ID, (row.City, row.Street, row.StrDate, row.Reason))

    def send(self, user_id, msg):
        try:
            self.bot.send_message(user_id, u'Внимание отключение!\n\n'
                                      u'Населенный пункт: %s\n'
                                      u'Улица: %s\n'
                                      u'Время отключения: %s\n'
                                      u'Причина: %s\n' % (msg))
        except Exception as e:
            logger.error('something wrong: %s' % e)
        logger.info('done')


def main():
    sc = Scheduler()
    #sc.send()

if __name__ == '__main__':
    main()
