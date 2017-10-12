# -*- coding: utf-8 -*-
import os,sys
sys.path.insert(1, os.path.join(os.path.abspath('.'), 'Lib/site-packages'))
import telebot
from flask import request
import logger
from crawler import NotifyParser
import user as u
import time
import updater
import threading
from main import app
import config
COLS = [u'Населенный пункт', u'Улица', u'Время отключения', u'Причина']
cmds = {u'Подписаться':'notify', u'Отписаться':'unnotify', u'Помощь':'start', u'Показать ближайшее':'show', u'Показать по подписке':'showmy'}

logger = logger.logger()

bot = telebot.TeleBot(config.token, threaded = False)

user_dict = {}

if config.heroku_debug:
    logger.debug('remote debug')
    sys.path.append('/app/pycharm-debug.egg')
    import pydevd
    pydevd.settrace(config.server_debug, port=config.port_debug, stdoutToServer=True, stderrToServer=True)

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

def global_kbd():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_a = telebot.types.KeyboardButton('Подписаться')
    btn_b = telebot.types.KeyboardButton('Показать ближайшее')
    btn_c = telebot.types.KeyboardButton('Отписаться')
    btn_d = telebot.types.KeyboardButton('Показать по подписке')
    markup.add(btn_a, btn_b)
    markup.add(btn_c, btn_d)
    return markup

def put_outage(user_id, ntf, mrkup):
    s = ''
    for line in ntf:
        l = zip(COLS, line)
        for name, value in l:
            if name == COLS[2]:
                value = u.get_date(value)
            if type(value) == str:
                value = unicode(value.decode('utf-8'))
            s += u'%s: %s\n' % (name, value)
        s += u'\n\n'
    bot.send_message(user_id, s, reply_markup = mrkup)

@bot.message_handler(commands=['help', 'start'])
def start(message):
    mrkup = global_kbd()
    bot.send_message(message.chat.id, u'Добро пожаловать %s. Данный бот поможет вам узнать о плановом отключении элетричества или подписаться на уведомление о плановом отключении. '
                                      u'\nПодписаться на уведомление нужно выполнить команду /notify '
                                      u'\nУзнать будет ли отключение нужно выполнить команду /show' % message.from_user.first_name, reply_markup = mrkup)

@bot.message_handler(commands=['showmy'])
def showmy(message):
    user_dict[message.chat.id] = u.User(message.chat.id)
    ntf = user_dict[message.chat.id].notifies()
    mrkup = global_kbd()
    if not ntf:
        bot.send_message(message.chat.id, u'У вас пока нет подписок на уведомление', reply_markup = mrkup)
    else:
        outage = u.get_useroutage2(message.chat.id)
        if not outage:
            bot.send_message(message.chat.id, u'В ближайшее время не будет отключений!', reply_markup = mrkup)
        else:
            ntf = []
            for row in outage:
                ntf.append([row.City, row.Street, row.StrDate, row.Reason])
            put_outage(message.chat.id, ntf, mrkup)

@bot.message_handler(commands=['unnotify'])
def unnotify(message):
    user_dict[message.chat.id] = u.User(message.chat.id)
    ntf = user_dict[message.chat.id].notifies
    mrkup = global_kbd()
    if not ntf:
        bot.send_message(message.chat.id, u'У вас пока нет подписок на уведомление', reply_markup = mrkup)
    else:
        s = u''
        i = 1
        for n in ntf:
            s += u'%d. Населенный пункт: %s, Улица: %s, Кол-во дней: %d\n' % (i, n.city, n.street, n.notify)
            i += 1

    bot.send_message(message.chat.id, u'Введите номер уведомления которое нужно удалить:\n' + s)
    bot.register_next_step_handler(message, process_unnotify_step)

@check_break
def process_unnotify_step(message):
    user = user_dict[message.chat.id]
    id = message.text.strip()
    try:
        if not int(id) in range(1, len(user.notifies) + 1):
            bot.reply_to(message, 'Не правильно указан номер уведомления.')
            bot.register_next_step_handler(message, process_unnotify_step)
        else:
            user.notifies.delete(idx=int(id)-1)
            mrkup = global_kbd()
            bot.send_message(message.chat.id, 'Уведомление удалено', reply_markup = mrkup)
    except ValueError:
        bot.reply_to(message, 'Не правильно указан номер уведомления.')
        bot.register_next_step_handler(message, process_unnotify_step)

@bot.message_handler(commands=['notify'])
def notify(message):
    user_dict[message.chat.id] = u.Notify()
    bot.send_message(message.chat.id, u'Чтобы получать уведомления об отключении нужно указать населенный пункт, улицу и количество дней до которого нужно будет уведомить'
                                      u'\n\nДля начала укажите населенный пункт без сокращений и аббревиатур, например: Беломестное или Белгород')
    bot.register_next_step_handler(message, process_city_step)

@check_break
def process_city_step(message):
    try:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn_a = telebot.types.KeyboardButton('Все')
        notify = user_dict[message.chat.id]
        notify.city = message.text.strip()
        user_dict[message.chat.id] = notify
        markup.add(btn_a)
        bot.send_message(message.chat.id, u'Далее укажите улицу без сокращений и аббревиатур, например: Центральная или Спортивная', reply_markup = markup)
        bot.register_next_step_handler(message, process_street_step)
    except:
        bot.reply_to(message, 'Не правильно указана Улица. Попробуйте снова.')
        bot.register_next_step_handler(message, process_city_step)

@check_break
def process_street_step(message):
    try:
        notify = user_dict[message.chat.id]
        notify.street = message.text.strip()
        user_dict[message.chat.id] = notify
        # если нужно просто показать событие
        if user_dict[message.chat.id].show:
            msg, ntf = NotifyParser().get_outage(user_dict[message.chat.id].city, user_dict[message.chat.id].street)
            mrkup = global_kbd()
            if msg:
                logger.warn(msg)
                bot.send_message(message.chat.id, msg, reply_markup = mrkup)
            else:
                if not ntf:
                    bot.send_message(message.chat.id, 'В этом месяце нет информации по отключению по этому адресу', reply_markup = mrkup)
                    return
                put_outage(message.chat.id, ntf, mrkup)
        # если нужно добавить событие
        else:
            bot.send_message(message.chat.id, u'Теперь укажите за сколько дней до отключения нужно Вас уведомить(от 1 до 3 дней). Введите 1, 2 или 3.')
            bot.register_next_step_handler(message, process_notify_step)
    except:
        bot.reply_to(message, 'Не правильно указана Улица. Попробуйте снова.')
        bot.register_next_step_handler(message, process_street_step)

@check_break
def process_notify_step(message):
    try:
        notify = user_dict[message.chat.id]
        notify.notify = int(message.text.strip())

        chk = notify.exist(message.chat.id)
        if chk:
            bot.send_message(message.chat.id, 'Вы уже подписаны на данное уведомление')
        else:
            notify.save(message.chat.id)
            mrkup = global_kbd()
            bot.send_message(message.chat.id, u'Вы подписались на уведомление.', reply_markup = mrkup)
            updater.main()
    except ValueError:
        bot.reply_to(message, 'Укажите число от 1 до 3')
        bot.register_next_step_handler(message, process_notify_step)
    except:
        bot.reply_to(message, 'Что-то пошло не так. Попробуйте снова.')
        bot.register_next_step_handler(message, process_notify_step)

@bot.message_handler(commands=['show'])
def show(message):
    user_dict[message.chat.id] = u.Notify()
    user_dict[message.chat.id].show = True
    bot.send_message(message.chat.id, u'Чтобы узнать о ближайшем отключении нужно указать населенный пункт и улицу'
                     u'\n\nДля начала укажите населенный пункт без сокращений и аббревиатур, например: Беломестное или Белгород')
    bot.register_next_step_handler(message, process_city_step)

@bot.message_handler(func=lambda message: message.text == u"Подписаться")
def command_text_notify(message):
    return u'subscribe', 200
    notify(message)
    
@bot.message_handler(func=lambda message: message.text == u"Отписаться")
def command_text_notify(message):
    unnotify(message)

@bot.message_handler(func=lambda message: message.text == u"Показать ближайшее")
def command_text_notify(message):
    show(message)

@bot.message_handler(func=lambda message: message.text == u"Показать по подписке")
def command_text_notify(message):
    showmy(message)

@bot.message_handler(func=lambda message: message.text == u"Помощь")
def command_text_notify(message):
    start(message)

@app.route(config.WEBHOOK_URL_PATH, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route("/", methods=['GET', 'HEAD'])
def index():
    return 'ok', 200

def webhook():
    bot.remove_webhook()
    time.sleep(3) #needed pause between commands
    bot.set_webhook(url=config.WEBHOOK_URL_BASE)
    return "!", 200

def polling():
    bot.polling(none_stop=False, interval=2)

if config.host == 'gae':
    #устанавливать вебхук когда мы на хероку
    #app.run(host=config.WEBHOOK_LISTEN, port=config.WEBHOOK_PORT)

    webhook()
elif config.host == 'local':
    bot.remove_webhook()
    t1_stop = threading.Event()
    t1 = threading.Thread(target=polling)
    t1.start()

