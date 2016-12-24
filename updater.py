# -*- coding: utf-8 -*-
import settings
from crawler import NotifyParser
from db import db
import re
from datetime import datetime


dates = '\d{4}-\d{2}-\d{2}|\d{2}.\d{2}.\d{4}|\d{2}.\d{2}.\d{2}|\d{2} \W* \d{4}'
def main():
    #get all outage from site
    msg, ls = NotifyParser().get_all()
    if msg:
        raise msg
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
            print 'no records in db'
        #get all outage from db
        cur.execute('select * from public."ElectroOutage"')
        rows = cur.fetchall()
        outage = {}
        if rows:
            for row in rows:
                outage[row[1]] = [row[2], row[3], row[4], row[5], row[6]]
        #merge
        for user in usernotify:
            exist_list = {} # list of all notifies on site
            for notify in usernotify:
                for l in ls:
                    if unicode(usernotify[notify][1].decode('utf-8')).lower() in l[0].lower() and unicode(usernotify[notify][2].decode('utf-8')).lower() in l[1].lower():
                        date_line = re.findall(dates, l[2].lower())
                        if date_line[0]:
                            for old, new in [(u'января', '01'), (u'февраля', '02'), (u'марта', '03'), (u'апреля', '04'), (u'мая', '05'), (u'июня', '06'), (u'июля', '07'), (u'августа', '08'), (u'сентября', '09'), (u'октября', '10'), (u'ноября', '11'), (u'декабря', '12')]:
                                date_str = date_line[0].replace(old, new)
                            date_str = date_str.replace(' ', '.')
                            exist_list[usernotify[notify][0]] = [l[0].encode('utf8'), l[1].encode('utf8'), date_str.encode('utf8'), l[2].encode('utf8'), l[3].encode('utf8')]
        if exist_list:
            sql_add = ''
            sql_del = ''
            if not outage:
                sql_add = 'insert into public."ElectroOutage" ("UserNotify_ID", "City", "Street", "Date", "StrDate", "Reason") values '
                for exist in exist_list:
                        sql_add += '''(%d, '%s', '%s', '%s', '%s', '%s'),''' % (exist, exist_list[exist][0], exist_list[exist][1], exist_list[exist][2], exist_list[exist][3], exist_list[exist][4])
                sql_add = sql_add[:-1] + ';'
            else:
                #add
                sql_add_header = 'insert into public."ElectroOutage" ("UserNotify_ID", "City", "Street", "Date", "StrDate", "Reason") values '
                header = False
                for exist in exist_list:
                    add = True
                    existr = [exist, exist_list[exist][0], exist_list[exist][1], exist_list[exist][2], exist_list[exist][3]]
                    for row in outage:
                        if existr == [row, outage[row][0], outage[row][1], outage[row][2].strftime('%d.%m.%Y'), outage[row][3]]:
                            add = False
                            break
                    if add:
                        if not header:
                            sql_add += sql_add_header
                            header = True
                        sql_add += '''(%d, '%s', '%s', '%s', '%s', '%s'),''' % (exist, exist_list[exist][0], exist_list[exist][1], exist_list[exist][2], exist_list[exist][3], exist_list[exist][4])
                if sql_add:
                    sql_add = sql_add[:-1] + ';'
                #del
                for row in outage:
                    delete = False
                    rowr = [row, outage[row][0], outage[row][1], outage[row][2].strftime('%d.%m.%Y'), outage[row][3]]
                    for exist in exist_list:
                        if rowr == [exist, exist_list[exist][0], exist_list[exist][1], exist_list[exist][2], exist_list[exist][3]]:
                            delete = True
                            break
                    if delete:
                        sql_del += '''delete from public."ElectroOutage" e where  e."UserNotify_ID" = %d and e."City" = '%s' and e."Street" = '%s' and e."StrDate" = '%s';\n''' % (exist, exist_list[exist][0], exist_list[exist][1], exist_list[exist][3])
            if sql_add:
                try:
                    cur.execute(sql_add)
                    dba.conn.commit()
                except:
                    dba.conn.rollback()
            if sql_del:
                try:
                    cur.execute(sql_del)
                    dba.conn.commit()
                except:
                    dba.conn.rollback()
    finally:
        dba.disconnect()


if __name__ == '__main__':
    main()