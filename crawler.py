# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import os
import re
URL = os.environ.get('MRSKURL')

class NotifyParser():

    def __init__(self, city, street):
        self.city = city
        self.street = street

    def parse(self):
        try:
            r = requests.get(URL)
            soup = BeautifulSoup(r.text)
            ls = soup.find_all('tr', id=re.compile('^ufid.*'))

            if ls:
                notify = []
                for item in ls:
                    if self.city.lower() in item.contents[1].text.lower() and self.street.lower() in  item.contents[3].text.lower():
                        city = item.contents[1].text
                        street = item.contents[3].text
                        date_range = item.contents[5].text
                        reason = item.contents[7].text
                        notify.append([city, street, date_range, reason])
            return '', notify
        except:
            return 'Сервис временно не доступен', []

