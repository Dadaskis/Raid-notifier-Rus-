# pip install python-telegram-bot --upgrade

from telegram.ext import Updater
from telegram.ext import CommandHandler
import pickle
import datetime
from dateutil import tz
import pytz

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

updater = Updater(token='1693637599:AAFOoMBysdzdmE-4X4Rdlijv47OCyZqC_aA', use_context=True)

dispatcher = updater.dispatcher

def newline_text(*args):
	result = ""
	for text in args:
		result += text + "\n"
	return result

HELP_TEXT = newline_text(
	"Этот бот предназначен для рейдеров-масонов.",
	"/create_notification [time] [message] - создаёт уведомление. Вместо [time] пишем точное время посылки уведомления в формате [День].[Месяц].[Год].[Час].[Минута], обязательно через точку. Время по Москве. Вместо [message] любое сообщение.",
	"/follow - подписаться на рассылки, работает только когда у тебя есть никнейм",
	"/unfollow - отписаться от рассылки и быть казнённым на алтаре"
)
time_format = "%d.%m.%Y.%H.%M"
notifications_check_delay = 1

nicknames = []
notifications = []

class Notification:
	def __init__(self):
		self.time = datetime.datetime.now()
		self.message = ""
		self.chat = 0

try:
	nicknames = pickle.load(open("nicknames.data", "rb"))
except:
	print("Cant read nicknames")

try:
	notifications = pickle.load(open("notifications.data", "rb"))
except:
	print("Cant read notifications")

def save_nicks():
	pickle.dump(nicknames, open("nicknames.data", "wb"))

def save_nick(update):
    nick = update.message.from_user.username
    if not nick in nicknames:
    	nicknames.append(nick)
    	save_nicks()

def remove_nick(update):
    nick = update.message.from_user.username
    nicknames.remove(nick)
    save_nicks()

def save_notifications():
	pickle.dump(notifications, open("notifications.data", "wb"))

def save_notification(time, message, chat):
	global time_format
	notification = Notification()
	notification.time = time
	notification.message = message
	notification.chat = chat
	notifications.append(notification)
	save_notifications()

def time_difference(first_time, later_time):
	difference = later_time - first_time
	seconds_in_day = 24 * 60 * 60
	datetime.timedelta(0, 8, 562000)
	div = divmod(difference.days * seconds_in_day + difference.seconds, 60)
	return (div[0] * 60) + div[1]

def check_notifications():
	global time_format
	global updater
	for notification in notifications:
		seconds = time_difference(datetime.datetime.now(tz.gettz("Europe/Moscow")), notification.time)
		#print(str(seconds) + " " + notification.message)
		if seconds <= 0:
			message = notification.message + "\n\n"
			for nick in nicknames:
				message += " @" + nick + " "
			updater.bot.send_message(notification.chat, message)
			notifications.remove(notification)
			save_notifications()
		

def send_to_chat(context, update, text):
    context.bot.send_message(chat_id = update.effective_chat.id, text = text)
    
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Пиши /help")
    
def help(update, context):
	global HELP_TEXT
	send_to_chat(context, update, HELP_TEXT)

def follow(update, context):
	save_nick(update)
	send_to_chat(context, update, "@" + update.message.from_user.username + " подписался")
	
def unfollow(update, context):
	remove_nick(update)
	send_to_chat(context, update, "@" + update.message.from_user.username + " отписался, приносим его в жертву ради бога рейдов")

def create_notification(update, context):
	global time_format
	text = update.message.text
	text = text.replace("/create_notification", "").strip()
	time_string = text.split()[0]
	time = datetime.datetime.strptime(time_string, time_format)
	timezone = pytz.timezone("Europe/Moscow")
	time = timezone.localize(time, is_dst = None).astimezone(tz.gettz("Europe/Moscow"))
	message = text.replace(time_string, "").strip()
	save_notification(time, message, update.effective_chat.id)
	send_to_chat(context, update, "Осталось до обьявления: " + str(time - datetime.datetime.now(tz.gettz("Europe/Moscow"))))
	

commands = [start, help, follow, unfollow, create_notification]
for command in commands:
	handler = CommandHandler(command.__name__, command)
	dispatcher.add_handler(handler)

print("Start")

import threading

def calling_check_notifications():
	threading.Timer(notifications_check_delay, calling_check_notifications).start()
	check_notifications()
calling_check_notifications()

updater.start_polling()
