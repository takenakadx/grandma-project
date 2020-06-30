import queue
import json
import time
import threading
import traceback
import lib.DataBase as DBL
from datetime import datetime
from lib.Web import python_web_server,MyHTTPRequestHandler
import lib.Line_api as LAPI
import lib.Sheet_edit as SAPI
import lib.Voice as Voice
import os
from contextlib import redirect_stdout

def web_starter(dd,q,*args):
	webserver = python_web_server((dd["ip"],dd["port"]),MyHTTPRequestHandler,q,*args)
	webserver.serve_forever()

def main(initialize_data):
	print("main thread started")
	finish_event = threading.Event()

	data = {'data':queue.Queue(),'request':queue.Queue(),'voice':queue.Queue(),'line':queue.Queue()}
	data["data"].put({"time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"dataType":"log","importance":"notice","title":"start","body1":"started program","thread":"main"})

	db = DBL.DataBase(finish_event,data,initialize_data["DB"])
	web_thread = threading.Thread(target=web_starter,args=[initialize_data["web"],data],daemon=True)
	sheet_thread = SAPI.SheetEditor(data,finish_event,initialize_data["sheet"])
	voice_thread = Voice.Say(data,finish_event,initialize_data["voice"])
	
	sheet_thread.start()
	web_thread.start()
	voice_thread.start()
	db.start()

	while True:
		try:
			time.sleep(0.01)
		except KeyboardInterrupt:
			finish_event.set()
			break

if __name__ == '__main__':
	setting = dict()
	if not os.path.exists('settings.json'):
		new_setting = {"DB":None,"web":None,"sheet":None,"voice":None}
		new_setting["DB"] = {"sqlite":{"active":False,"path":"datafiles/data.db","tables":{},"uniques":{},"delete":{"active":False,"hours":0},"wait_time":1}}
		new_setting["web"] = {"ip":"localhost","port":80}
		new_setting["sheet"] = {"active":False,"waittime":20,"sheet_url":"","certification":"","key":[]}
		with open('settings.json','w') as f:
			f.write(json.dumps(new_setting,indent=2))
	with open('settings.json') as f:
		setting = json.load(f)
	main(setting)
