# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import os
import re
URL = os.environ.get('MRSKURL')
vary_strange_streets = [u'все', u'всё', u'быт', u'все улицы', u'все, кто будет обращаться', u'все объекты']
class NotifyParser():

    def __init__(self):
        self.city = None
        self.street = None

    def check_street(self, street):
        ins = False
        for s in vary_strange_streets:
            if s in street:
                ins = True
                break
        return (self.street.lower() in street) or ins

    def parse(self, url):
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.text)
            ls = soup.find_all('tr', id=re.compile('^ufid.*'))
            return ls
        except:
            return []

    def get_all(self):
        try:
            ls = self.parse(URL)
            if ls:
                notify = []
                for item in ls:
                    city = item.contents[1].text
                    street = item.contents[3].text
                    date_range = item.contents[5].text
                    reason = item.contents[7].text
                    notify.append([city, street, date_range, reason])
                return '', notify
            return 'Не удалось получить информацию с сайта', []
        except:
            return 'ошибка при получении информации', []

    def get_outage(self, city, street):
        try:
            self.city = city
            self.street = street
            ls = self.parse(URL)
            if ls:
                notify = []
                for item in ls:
                    if self.city.lower() in item.contents[1].text.lower():
                        if self.check_street(item.contents[3].text.lower()):
                            city = item.contents[1].text
                            street = item.contents[3].text
                            date_range = item.contents[5].text
                            reason = item.contents[7].text
                            notify.append([city, street, date_range, reason])
                return '', notify
            return 'Не удалось получить информацию с сайта', []
        except:
            return 'Сервис временно не доступен', []

