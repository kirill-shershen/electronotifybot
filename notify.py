# -*- coding: utf-8 -*-
import telebot
from flask import Flask, request
import settings
import logging
import db
import crawler
from datetime import date

loglevel = logging.DEBUG == settings.debug
logging.getLogger('requests').setLevel(loglevel)
logging.basicConfig(format='[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s', level=logging.INFO
                    , datefmt='%d.%m.%Y %H:%M:%S')

COLS = [u'Населенный пункт', u'Улица', u'Время отключения', u'Причина']
cmds = {u'Подписаться':'notify', u'Отписаться':'unnotify', u'Помощь':'start', u'Показать ближайшее':'show'}
class server:
    def route(self, *args, **kwargs):
        def decorator(f):
            return f

        return decorator

bot = telebot.TeleBot(settings.token)

if settings.debug:
    server = server()
else:
    server = Flask(__name__)

class User:
    def __init__(self, id):
        self.id = id
        self.city = None
        self.street = None
        self.notify = None
        self.db = db.db()
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
            self.db.rollback()
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
            self.db.rollback()
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

user_dict = {}

def do_command(message):
    # getattr(sys.modules[__name__], cmds[message.text])(message)
    pass

def check_break(func):
    '''Проверяем что не было вызова новой операции'''
    def decorate(message):
        if message.text in cmds.keys():
            do_command(message)
        else:
            func(message)
    return decorate

@bot.message_handler(commands=['help', 'start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_a = telebot.types.KeyboardButton('Подписаться')
    btn_b = telebot.types.KeyboardButton('Показать ближайшее')
    btn_c = telebot.types.KeyboardButton('Отписаться')
    btn_d = telebot.types.KeyboardButton('Помощь')
    markup.add(btn_a, btn_b)
    markup.add(btn_c, btn_d)
    bot.send_message(message.chat.id, u'Добро пожаловать %s. Данный бот поможет вам узнать о плановом отключении элетричества или подписаться на уведомление о плановом отключении. '
                                      u'\nПодписаться на уведомление нужно выполнить команду /notify '
                                      u'\nУзнать будет ли отключение нужно выполнить команду /show' % message.from_user.first_name, reply_markup = markup)

@bot.message_handler(commands=['unnotify'])
def unnotify(message):
    user_dict[message.chat.id] = User(message.chat.id)
    ntf = user_dict[message.chat.id].notifies()
    if not ntf:
        bot.send_message(message.chat.id, u'У вас пока нет подписок на уведомление')
    else:
        s = u''
        i = 1
        for n in ntf:
            l = zip([u'Населенный пункт', u'Улица', u'Кол-во  дней'], ntf[n])
            s += u'%d. ' % i
            for name, value in l:
                s += u'%s: %s, ' % (name, unicode(str(value).decode('utf-8')))
            i += 1
            s = s[:-2] + '\n'

    bot.send_message(message.chat.id, u'Введите номер уведомления которое нужно удалить:\n' + s)
    bot.register_next_step_handler(message, process_unnotify_step)

@check_break
def process_unnotify_step(message):
    user = user_dict[message.chat.id]
    id = message.text.strip()
    try:
        if not int(id) in range(1, len(user.ListNotify) + 1):
            bot.reply_to(message, 'Не правильно указан номер уведомления.')
            bot.register_next_step_handler(message, process_unnotify_step)
        else:
            user.delete(user.ListNotify[int(id)-1])
            bot.send_message(message.chat.id, 'Уведомление удалено')
    except ValueError:
        bot.reply_to(message, 'Не правильно указан номер уведомления.')
        bot.register_next_step_handler(message, process_unnotify_step)

@bot.message_handler(commands=['notify'])
def notify(message):
    user_dict[message.chat.id] = User(message.chat.id)
    bot.send_message(message.chat.id, u'Чтобы получать уведомления об отключении нужно указать населенный пункт, улицу и количество дней до которого нужно будет уведомить'
                                      u'\n\nДля начала укажите населенный пункт без сокращений и аббревиатур, например: Беломестное или Белгород')
    bot.register_next_step_handler(message, process_city_step)

@check_break
def process_city_step(message):
    try:
        user = user_dict[message.chat.id]
        user.city = message.text.strip()
        user_dict[message.chat.id] = user
        bot.send_message(message.chat.id, u'Далее укажите улицу без сокращений и аббревиатур, например: Центральная или Спортивная')
        bot.register_next_step_handler(message, process_street_step)
    except:
        bot.reply_to(message, 'Не правильно указана Улица. Попробуйте снова.')
        bot.register_next_step_handler(message, process_city_step)

@check_break
def process_street_step(message):
    try:
        user = user_dict[message.chat.id]
        user.street = message.text.strip()
        user_dict[message.chat.id] = user
        if user_dict[message.chat.id].show:
            msg, ntf = crawler.NotifyParser(user_dict[message.chat.id].city, user_dict[message.chat.id].street).parse()
            if msg:
                bot.send_message(message.chat.id, msg)
            else:
                if not ntf:
                    bot.send_message(message.chat.id, 'В этом месяце нет информации по отключению по этому адресу')
                    return
                s = ''
                for line in ntf:
                    l = zip(COLS, line)
                    for name, value in l:
                        #ставим пробел между датой и временем
                        year = str(date.today().year)
                        if year in value and value[value.find(year)+4] != ' ':
                            value = value.replace(year, year + ' ')
                        s += u'%s: %s\n' % (name, value)
                    s += u'\n\n'
                bot.send_message(message.chat.id, s)
        else:
            bot.send_message(message.chat.id, u'Теперь укажите за сколько дней до отключения нужно Вас уведомить(от 1 до 3 дней). Введите 1, 2 или 3.')
            bot.register_next_step_handler(message, process_notify_step)
    except:
        bot.reply_to(message, 'Не правильно указана Улица. Попробуйте снова.')
        bot.register_next_step_handler(message, process_street_step)

@check_break
def process_notify_step(message):
    try:
        user = user_dict[message.chat.id]
        user.notify = message.text.strip()
        user.notify = int(user.notify)

        msg, chk = user.check()
        if not chk and msg:
            bot.send_message(message.chat.id, msg)
        else:
            user.save()
            bot.send_message(message.chat.id, u'Вы подписались на уведомление.')
    except ValueError:
        bot.reply_to(message, 'Укажите число от 1 до 3')
        bot.register_next_step_handler(message, process_notify_step)
    except:
        bot.reply_to(message, 'Что-то пошло не так. Попробуйте снова.')
        bot.register_next_step_handler(message, process_notify_step)

@bot.message_handler(commands=['show'])
def show(message):
    user_dict[message.chat.id] = User(message.chat.id)
    user_dict[message.chat.id].show = True
    bot.send_message(message.chat.id, u'Чтобы узнать о ближайшем отключении нужно указать населенный пункт и улицу'
                     u'\n\nДля начала укажите населенный пункт без сокращений и аббревиатур, например: Беломестное или Белгород')
    bot.register_next_step_handler(message, process_city_step)

@bot.message_handler(func=lambda message: message.text == u"Подписаться")
def command_text_notify(message):
    notify(message)

@bot.message_handler(func=lambda message: message.text == u"Отписаться")
def command_text_notify(message):
    unnotify(message)

@bot.message_handler(func=lambda message: message.text == u"Показать ближайшее")
def command_text_notify(message):
    show(message)

@bot.message_handler(func=lambda message: message.text == u"Помощь")
def command_text_notify(message):
    start(message)

@server.route("/bot", methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=settings.WEBHOOK_URL_BASE)
    return "!", 200

if not settings.debug:
    #устанавливать вебхук когда мы на хероку
    webhook()
    server.run(host=settings.WEBHOOK_LISTEN, port=settings.WEBHOOK_PORT)
    server = Flask(__name__)
else:
    bot.remove_webhook()
    bot.polling()