# -*- coding: utf-8 -*-

import settings
from datetime import datetime
import telebot
import user as u

class Scheduler():

    def __init__(self):
        self.events = {}
        self.prepare()

    def prepare(self):
        usernotify = u.get_notify()
        outage = u.get_outage()
        date = datetime.now().date()
        for user in usernotify:
            self.events[user] = []
            for out in outage:
                if abs((date - outage[out][2]).days) == usernotify[user][3] and (usernotify[user][0] == out):
                    self.events[user].append([outage[out][0], outage[out][1], outage[out][3], outage[out][4]])

    def send(self):
        if not self.events:
            return 'nothing to send'

        bot = telebot.TeleBot(settings.token)
        for ev in self.events:
            if self.events[ev]:
                for msg in self.events[ev]:
                    bot.send_message(ev, 'Внимание отключение!\n\n'
                                     'Населенный пункт: %s\n'
                                     'Улица: %s\n'
                                     'Время отключения: %s\n'
                                     'Причина: %s\n' % (msg[0], msg[1], u.get_date(msg[2]), msg[3]))


def main():
    sc = Scheduler()
    sc.send()

if __name__ == '__main__':
    main()