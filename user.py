# -*- coding: utf-8 -*-
from db import db
from datetime import date
import settings

logger = settings.logger()

def get_date(str_date):
    #ставим пробел между датой и временем
    year = str(date.today().year)
    if year in str_date and str_date[str_date.find(year)+4] != ' ':
        return str_date.replace(year, year + ' ')

def get_notify():
    try:
        dba = db()
        dba.connect()
        cur = dba.conn.cursor()
        cur.execute('select * from public."UserNotify"')
        rows = cur.fetchall()
        usernotify = {}
        if rows:
            for row in rows:
                usernotify[row[0]] = [row[4], row[1], row[2], row[3]]
        if not rows or not usernotify:
            logger.warning('no records in db')
            exit(0)
        return usernotify
    finally:
        dba.disconnect()

def get_useroutage(user_id = None):
    try:
        sql_where = ''
        if user_id:
            sql_where = ' e where e."UserNotify_ID" in (select u."ID" from public."UserNotify" u where u."User_ID" = %d)' % user_id
        dba = db()
        dba.connect()
        cur = dba.conn.cursor()
        cur.execute('select * from public."ElectroOutage" %s;' % sql_where)
        rows = cur.fetchall()
        outage = {}
        if rows:
            for row in rows:
                outage[row[1]] = [row[2], row[3], row[4], row[5], row[6]]
        return outage
    finally:
        dba.disconnect()

class UserNotify:
    def __init__(self, id):
        self.id = id
        self.city = None
        self.street = None
        self.notify = None
        self.db = db()
        self.show = False
        self.ListNotify = []

    def check(self):
        res = self.id and self.city and self.street and self.notify
        select_cnt = '''select count(*) from public."UserNotify" u
where
  u."User_ID" = %d and
  u."City" = '%s' and
  u."Street" = '%s' and
  u."Notify" = %d'''
        try:
            self.db.connect()
            cur = self.db.conn.cursor()
            cur.execute(select_cnt % (self.id, self.city.encode('utf8'), self.street.encode('utf8'), self.notify ))
            row = cur.fetchone()
            if int(row[0]) > 0:
                str = 'Вы уже подписаны на данное уведомление'
                return str, False
        except:
            self.db.disconnect()
        return '', res

    def save(self):
        try:
            self.db.connect()
            cur = self.db.conn.cursor()
            sql_ins = '''insert into public."UserNotify"("User_ID", "City", "Street", "Notify")
                          values (%d, '%s', '%s', %d);''' %(self.id, self.city.encode('utf8'), self.street.encode('utf8'), self.notify)
            cur.execute(sql_ins)
            self.db.conn.commit()
        except:
            self.db.conn.rollback()
        finally:
            self.db.disconnect()

    def update(self):
        pass

    def delete(self, id):
        try:
            self.db.connect()
            cur = self.db.conn.cursor()
            sql_ins = '''delete from public."UserNotify" u where u."ID" = %d;''' % (id)
            cur.execute(sql_ins)
            self.db.conn.commit()
        except:
            self.db.conn.rollback()
        finally:
            self.db.disconnect()

    def notifies(self):
        try:
            self.db.connect()
            cur = self.db.conn.cursor()
            select_sql = '''select * from public."UserNotify" u where u."User_ID" = %d '''
            cur.execute(select_sql % (self.id))
            if cur.rowcount == 0:
                return []
            else:
                rows = cur.fetchall()
                res = {}
                for row in rows:
                    res[row[4]] = [row[1], row[2], row[3]]
                self.ListNotify = res.keys()
                return res
        except:
            self.db.disconnect()
