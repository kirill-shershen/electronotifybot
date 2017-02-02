# -*- coding: utf-8 -*-

import settings
from datetime import datetime
import telebot
import user as u

logger = settings.logger()

class Scheduler():

    def __init__(self):
        self.events = {}
        self.prepare()

    def prepare(self):
        usernotify = u.get_notify()
        outage = u.get_useroutage()
        date = datetime.now().date()
        for user in usernotify:
            self.events[user] = []
            for row in outage:
                for out in outage[row]:
                    if abs((date - out[2]).days) == usernotify[user][3] and (usernotify[user][0] == row):
                        self.events[user].append([out[0], out[1], out[3], out[4]])

    def send(self):
        if not self.events:
            logger.info('nothing to send')
            return 'nothing to send'

        logger.info('sending messages...')
        try:
            bot = telebot.TeleBot(settings.token)
            for ev in self.events:
                if self.events[ev]:
                    for msg in self.events[ev]:
                        bot.send_message(ev, 'Внимание отключение!\n\n'
                                         'Населенный пункт: %s\n'
                                         'Улица: %s\n'
                                         'Время отключения: %s\n'
                                         'Причина: %s\n' % (msg[0], msg[1], u.get_date(msg[2]), msg[3]))
        except:
            logger.error('something wrong')
        logger.info('done')


def main():
    sc = Scheduler()
    sc.send()

if __name__ == '__main__':
    main()