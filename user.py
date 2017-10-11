# -*- coding: utf-8 -*-

from datetime import date
import logger
from models import ElectroOutage as eo
from models import UserNotify as un
from sqlalchemy.exc import SQLAlchemyError
logger = logger.logger()


def get_date(str_date):
    #ставим пробел между датой и временем
    year = str(date.today().year)
    if year in str_date and str_date[str_date.find(year)+4] != ' ':
        return str_date.replace(year, year + ' ')

def get_notify():
    pass
    # logger.debug('get_notify')
    # try:
    #     dba = DB()
    #     dba.connect()
    #     cur = dba.conn.cursor()
    #     cur.execute('select * from public."UserNotify"')
    #     rows = cur.fetchall()
    #     usernotify = {}
    #     if rows:
    #         for row in rows:
    #             usernotify[row[0]] = [row[4], row[1], row[2], row[3]]
    #     if not rows or not usernotify:
    #         logger.warning('no records in db')
    #         exit(0)
    #     return usernotify
    # finally:
    #     dba.disconnect()

def get_useroutage2(user_id = None):
    logger.debug('get_useroutage')
    if user_id:
        return eo.query.filter(eo.UserNotify_ID == un.ID).filter(un.User_ID == user_id).all()
    else:
        return eo.query.all()

def get_useroutage(user_id = None):
    pass
    # logger.debug('get_useroutage')
    # try:
    #     sql_where = ''
    #     if user_id:
    #         sql_where = ' e where e."UserNotify_ID" in (select u."ID" from public."UserNotify" u where u."User_ID" = %d)' % user_id
    #     dba = DB()
    #     dba.connect()
    #     cur = dba.conn.cursor()
    #     cur.execute('select * from public."ElectroOutage" %s;' % sql_where)
    #     rows = cur.fetchall()
    #     outage = {}
    #     if rows:
    #         for row in rows:
    #             if not outage.has_key(row[1]):
    #                 outage[row[1]] = list()
    #             outage[row[1]].append([row[2], row[3], row[4], row[5], row[6]])
    #     return outage
    # finally:
    #     dba.disconnect()

class Notify:

    def __init__(self, id = 0, city = '', street = '', notify = 0):
        self.id = id
        self.city = city
        self.street = street
        self.notify = notify
        self.show = False

    def save(self, user_id):
        n = un(user_id, self.city, self.street, self.notify)
        db.session.add(n)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
        self.id = n.ID

    def delete(self):
        un.query.filter_by(ID=self.id).delete()
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()

    def exist(self, user_id):
        return un.query.filter(un.User_ID == user_id).filter(un.City == self.city).filter(un.Street == self.street).filter(un.Notify == self.notify).count() > 0


class NotifyList:

    def __init__(self):
        self._list = []

    def load(self):
        ns = un.query.all()
        if ns:
            for n in ns:
                self.add(n.ID, n.City, n.Street, n.Notify)

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def __getitem__(self, item):
        return self._list[item]

    def add(self, id, city, street, notify):
        n = Notify(id, city, street, notify)
        self._list.append(n)
        return n

    def by_id(self, id):
        res = None
        for n in self._list:
            if n.id == id:
                res = n
                break
        return res

    def by_idx(self, idx):
        if idx >= 0 and idx < len(self._list):
            result = self._list[idx]
        else:
            result = None
        return result

    def delete(self, id = None, idx = None):
        n = None
        if not id is None:
            n = self.by_id(id)
        elif not idx is None:
            n = self._list[idx]
        if n:
            n.delete()
            self._list.remove(n)


class UserNotifyList(NotifyList):

    def __init__(self, id):
        NotifyList.__init__(self)
        self.user_id = id

    def load(self):
        ns = un.query.filter(un.User_ID == self.user_id).all()
        if ns:
            for n in ns:
                self.add(n.ID, n.City, n.Street, n.Notify)

    def new(self, city, street, notify):
        n = Notify(0, city, street, notify)
        n.save(self.user_id)
        self._list.append(n)


class Outage:

    def __init__(self, id = 0, usernotify_id = 0, city = '', street = '',date = None,  strdate = '', reason = ''):
        self.id = id
        self.usernotify_id = usernotify_id
        self.city = city
        self.street = street
        self.strdate = strdate
        self.date = date
        self.reason = reason

    def save(self):
        n = eo(self.usernotify_id, self.city, self.street, self.date, self.strdate, self.reason)
        db.session.add(n)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
        self.id = n.ID

    def delete(self):
        eo.query.filter_by(ID=self.id).delete()
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()

    def exist(self):
        return un.query.filter(eo.UserNotify_ID == self.usernotify_id).filter(eo.City == self.city).filter(eo.Street == self.street).filter(eo.Date == self.Date).filter(eo.StrDate == self.StrDate).filter(eo.Reason == self.Reason).count() > 0

class OutageList():

    def __init__(self):
        self._list = []

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def __getitem__(self, item):
        return self._list[item]

    def append(self, outage):
        if isinstance(outage, Outage):
            self._list.append(outage)

    def add(self, id, usernotify_id, city, street, date, strdate, reason):
        n = Outage(id, usernotify_id, city, street, date, strdate, reason)
        self._list.append(n)
        return n

    def load(self):
        ol = eo.query.all()
        if ol:
            for n in ol:
                self.add(n.ID, n.UserNotify_ID, n.City, n.Street, n.Date, n.StrDate, n.Reason)

    def delete(self, id = None, idx = None):
        n = None
        if not id is None:
            n = self.by_id(id)
        elif not idx is None:
            n = self._list[idx]
        if n:
            n.delete()
            self._list.remove(n)

    def find(self, usernotify_id, city, street, date, strdate, reason):
        res = 0
        for out in self._list:
            if [usernotify_id, city, street, date, strdate, reason] == [out.usernotify_id, out.city, out.street, out.date, out.strdate, out.reason]:
                res = out.id
                break
        return res

    def new(self, usernotify_id, city, street, date, strdate, reason):
        n = Outage(0, usernotify_id, city, street, date, strdate, reason)
        n.save(self.user_id)
        self._list.append(n)

    def by_id(self, id):
        res = None
        for n in self._list:
            if n.id == id:
                res = n
                break
        return res

    def by_idx(self, idx):
        if idx >= 0 and idx < len(self._list):
            result = self._list[idx]
        else:
            result = None
        return result


class User:

    def __init__(self, id):
        self.id = id
        self.notifies = UserNotifyList(id)
        self.outages = []
        self.show = False
        self.load_notifies()

    def load_notifies(self):
        self.notifies.load()


class UserNotify:
    def __init__(self, id):
        pass
#         self.id = id
#         self.city = None
#         self.street = None
#         self.notify = None
#         self.db = DB()
#         self.show = False
#         self.ListNotify = []
#
#     def check(self):
#         res = self.id and self.city and self.street and self.notify
#         select_cnt = '''select count(*) from public."UserNotify" u
# where
#   u."User_ID" = %d and
#   u."City" = '%s' and
#   u."Street" = '%s' and
#   u."Notify" = %d'''
#         try:
#             self.db.connect()
#             cur = self.db.conn.cursor()
#             cur.execute(select_cnt % (self.id, self.city.encode('utf8'), self.street.encode('utf8'), self.notify ))
#             row = cur.fetchone()
#             if int(row[0]) > 0:
#                 str = 'Вы уже подписаны на данное уведомление'
#                 return str, False
#         except:
#             self.db.disconnect()
#         return '', res
#
#     def save(self):
#         try:
#             self.db.connect()
#             cur = self.db.conn.cursor()
#             sql_ins = '''insert into public."UserNotify"("User_ID", "City", "Street", "Notify")
#                           values (%d, '%s', '%s', %d);''' %(self.id, self.city.encode('utf8'), self.street.encode('utf8'), self.notify)
#             cur.execute(sql_ins)
#             self.db.conn.commit()
#         except:
#             self.db.conn.rollback()
#         finally:
#             self.db.disconnect()
#
#     def update(self):
#         pass
#
#     def delete(self, id):
#         try:
#             self.db.connect()
#             cur = self.db.conn.cursor()
#             sql_ins = '''delete from public."UserNotify" u where u."ID" = %d;''' % (id)
#             cur.execute(sql_ins)
#             self.db.conn.commit()
#         except:
#             self.db.conn.rollback()
#         finally:
#             self.db.disconnect()
#
#     def notifies(self):
#         try:
#             self.db.connect()
#             cur = self.db.conn.cursor()
#             select_sql = '''select * from public."UserNotify" u where u."User_ID" = %d '''
#             cur.execute(select_sql % (self.id))
#             if cur.rowcount == 0:
#                 return []
#             else:
#                 rows = cur.fetchall()
#                 res = {}
#                 for row in rows:
#                     res[row[4]] = [row[1], row[2], row[3]]
#                 self.ListNotify = res.keys()
#                 return res
#         except:
#             self.db.disconnect()
