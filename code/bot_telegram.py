#-*- coding: utf-8 -*-
# window git https://git-scm.com/download/win
# pip install git+https://github.com/MoumenKhadr/telepot
import time
import telepot
from telepot.loop import MessageLoop
import os
import sys
import psutil
import threading
import config_key
import traceback
import json

TELEGRAM_BOT_ACCESS_TOKEN = config_key.TELEGRAM_BOT_ACCESS_TOKEN #'12234567:tttttttttttttttttttttttttttttt'  # 텔레그램으로부터 받은 Bot 토큰

bot = None
all_users = []
base_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data')
datafile = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/users.dat')


# Bot init
def init():
	global bot
	global all_users
	bot = telepot.Bot(TELEGRAM_BOT_ACCESS_TOKEN)
	MessageLoop(bot, handler_func).run_as_thread()
	if base_folder!='' and not os.path.exists(base_folder):
		os.makedirs(base_folder)
	all_users = load_users(datafile)
	wakeup_noti()

# Wakeup notification
def wakeup_noti():
	global all_users
	users=[]
	exception = False
	for user in all_users:
		try:
			bot.sendMessage(user, 'system restarted')
			users.append(user)
		except telepot.exception.BotWasBlockedError:
			exception = True
		except:
			traceback.print_exc()
			time.sleep(5)
			pass
	if exception == True :
		all_users = list(set(users))
		save_users(datafile,all_users)



def handler_func(msg):
	try:
		content_type, chat_type, chat_id = telepot.glance(msg)
		#print(content_type, chat_type, chat_id)
		find = False
		if content_type == 'text':
			for command in COMMANDS_LIST:
				if msg['text'].lower().strip() == command[0]:
					ret, data = command[1](content_type, chat_type, chat_id)
					if ret == True :
						bot.sendMessage(chat_id, data)
					find = True
			if find == False:
				bot.sendMessage(chat_id, 'not supported command')
	except:
		pass

# bot command meminfo
def meminfo(content_type, chat_type, chat_id):
	if sys.platform == 'win32':
		return True, 'not supported command on windows'
	memory_usage = os.popen("cat /proc/meminfo").read()
	return True, memory_usage

# bot command diskusage
def diskusage(content_type, chat_type, chat_id):
	obj_Disk = psutil.disk_usage('/')
	str = "Disk Total %5fGB\nDisk used %5fGB\nDisk Free %5fGB\nusage %4f%%"%((obj_Disk.total / (1024.0 ** 3)) , (obj_Disk.used / (1024.0 ** 3)) , (obj_Disk.free / (1024.0 ** 3)) , (obj_Disk.percent))
	return True, str

# bot command cpuinfo
def cpuinfo(content_type, chat_type, chat_id):
	if sys.platform == 'win32':
		return True, 'not supported command on windows'
	text1 = psutil.sensors_temperatures()
	text2 = psutil.cpu_stats()
	text3 = os.popen("uptime").read()
	return True, str(text1)+"\n"+str(text2) + "\n"+str(text3)
	
# bot command start_chat
def start_chat(content_type, chat_type, chat_id):
	global all_users
	print("start_chat")
	all_users.append(chat_id)
	all_users = list(set(all_users))
	print(all_users)
	save_users(datafile,all_users)
	return True, "system started"

COMMANDS_LIST=[('meminfo',meminfo),('/start',start_chat),('diskusage',diskusage),('cpuinfo',cpuinfo)]

def save_users(file,users):
	f = open(file,"w")
	json.dump(list(set(users)), f)
	f.close()
	os.chmod(file, 0o777)

def load_users(file):
	try:
		f = open(file,"r")
		users = json.load(f)
		f.close()
		return list(set(users))
	except:
		return []

def check_system_info(bot):
	obj_Disk = psutil.disk_usage('/')
	if obj_Disk.percent > 70 :
		# Warning
		for user in all_users:
			try:
				bot.sendMessage(user, 'Storage full:%f%%'%(obj_Disk.percent))
			except:
				pass

def thread(logger):
	init()
	# Main Loop
	print ('Listening ...')
	while(True):
		check_system_info(bot)
		time.sleep(60*60)# 1 hours

iThread = None

def Start(logger):
	global iThread
	iThread = threading.Thread(target=thread, args=[logger])
	iThread.daemon = True
	iThread.start()
	return iThread

if __name__ == "__main__":
	Start(None)
	while(True):
		time.sleep(60*60)

