# -*- coding: utf-8 -*-
import settings
from crawler import NotifyParser
from db import db
import re
from datetime import datetime
import user as u
import sys


logger = settings.logger()

dates = '\d{4}-\d{2}-\d{2}|\d{2}.\d{2}.\d{4}|\d{2}.\d{2}.\d{2}|\d{2} \W* \d{4}'
def main():
    dba = None
    #get all outage from site
    ls = NotifyParser().get_all()
    if not ls:
        exit(0)
    try:
        logger.debug(u'Чтение пользовательских настроек поиска')
        usernotify = u.get_notify()
        #get all outage from db
        logger.debug(u'Чтение уже созданных пользовательских уведомлений')
        outage = u.get_useroutage()
        #merge
        logger.debug(u'создание списка уведомлений')
        for user in usernotify:
            exist_list = {} # list of all notifies on site
            for notify in usernotify:
                for l in ls:
                    if unicode(usernotify[notify][1].decode('utf-8')).lower() in l[0].lower() and (unicode(usernotify[notify][2].decode('utf-8')).lower() in l[1].lower() or (unicode(usernotify[notify][2].decode('utf-8')).lower() == u'все')):
                        date_line = re.findall(dates, l[2].lower())
                        if date_line[0]:
                            for old, new in [(u'января', '01'), (u'февраля', '02'), (u'марта', '03'), (u'апреля', '04'), (u'мая', '05'), (u'июня', '06'), (u'июля', '07'), (u'августа', '08'), (u'сентября', '09'), (u'октября', '10'), (u'ноября', '11'), (u'декабря', '12')]:
                                date_str = date_line[0].replace(old, new)
                                break
                            date_str = date_str.replace(' ', '.')
                            exist_list[usernotify[notify][0]] = [l[0].encode('utf8'), l[1].encode('utf8'), date_str.encode('utf8'), l[2].encode('utf8'), l[3].encode('utf8')]
        if not exist_list:
            logger.info(u'Не найдено уведомлений для заданных настроек поиска')
        if exist_list:
            sql_add = ''
            sql_del = ''
            if not outage:
                logger.debug(u'Подготовка скрипта добавления')
                sql_add = 'insert into public."ElectroOutage" ("UserNotify_ID", "City", "Street", "Date", "StrDate", "Reason") values '
                for exist in exist_list:
                        sql_add += '''(%d, '%s', '%s', '%s', '%s', '%s'),''' % (exist, exist_list[exist][0], exist_list[exist][1], exist_list[exist][2], exist_list[exist][3], exist_list[exist][4])
                sql_add = sql_add[:-1] + ';'
                if not sql_add:
                    logger.debug(u'Нечего добавлять')
            else:
                #add
                logger.debug(u'Подготовка скрипта добавления')
                sql_add_header = 'insert into public."ElectroOutage" ("UserNotify_ID", "City", "Street", "Date", "StrDate", "Reason") values '
                header = False
                for exist in exist_list:
                    add = True
                    existr = [exist, exist_list[exist][0], exist_list[exist][1], exist_list[exist][2], exist_list[exist][3]]
                    for row in outage:
                        out_date = outage[row][2]
                        if existr == [row, outage[row][0], outage[row][1], out_date.strftime('%d.%m.%Y'), outage[row][3]] and out_date > datetime.now().date():
                            add = False
                            break
                    if add:
                        if not header:
                            sql_add += sql_add_header
                            header = True
                        sql_add += '''(%d, '%s', '%s', '%s', '%s', '%s'),''' % (exist, exist_list[exist][0], exist_list[exist][1], exist_list[exist][2], exist_list[exist][3], exist_list[exist][4])
                if sql_add:
                    sql_add = sql_add[:-1] + ';'
                else:
                    logger.debug(u'Нечего добавлять')
                #del
                logger.debug(u'Подготовка скрипта удаления')
                for row in outage:
                    delete = True
                    rowr = [row, outage[row][0], outage[row][1], outage[row][2].strftime('%d.%m.%Y'), outage[row][3]]
                    for exist in exist_list:
                        if rowr == [exist, exist_list[exist][0], exist_list[exist][1], exist_list[exist][2], exist_list[exist][3]]:
                            delete = False
                            break
                    if delete:
                        sql_del += '''delete from public."ElectroOutage" e where  e."UserNotify_ID" = %d and e."City" = '%s' and e."Street" = '%s' and e."StrDate" = '%s';\n''' % (row, outage[row][0], outage[row][1], outage[row][3])
                    if not sql_del:
                        logger.debug(u'Нечего удалять')
            if sql_add:
                try:
                    dba = db()
                    dba.connect()
                    cur = dba.conn.cursor()
                    logger.debug(u'Выполнение добавления')
                    logger.debug(unicode(sql_add.decode('utf-8')))
                    cur.execute(sql_add)
                    dba.conn.commit()
                except:
                    logger.error(u'Ошибка при выполнении скрипта добавления')
                    dba.conn.rollback()
            if sql_del:
                try:
                    dba = db()
                    dba.connect()
                    cur = dba.conn.cursor()
                    logger.debug(u'Выполнение удаления')
                    logger.debug(unicode(sql_del.decode('utf-8')))
                    cur.execute(sql_del)
                    dba.conn.commit()
                except:
                    logger.error(u'Ошибка при выполнении скрипта удаления')
                    dba.conn.rollback()
        logger.info(u'Обновление завершено')
    finally:
        if dba:
            dba.disconnect()


if __name__ == '__main__':
     if settings.heroku_debug:
         logger.debug('remote debug')
         sys.path.append('/app/pycharm-debug.egg')
         import pydevd
         pydevd.settrace(settings.server_debug, port=settings.port_debug, stdoutToServer=True, stderrToServer=True)
     logger.info('Обновление событий')
     main()