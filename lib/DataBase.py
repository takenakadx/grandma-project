import sqlite3
import os
import threading
import time
from datetime import datetime,timedelta
import traceback


#書き込み
#読み込み


#仕様
#dataにはdictを入れること
#tableにはlistを入れること
#tableの一番目はテーブル名
#cursorにはカーソルオブジェクトを入れること
#dataのkeyとtable[1:]は一致すること
def write_data_to_sqlite(data,table,column,cursor):
	try:
		execomand = "INSERT INTO {0}({1}) VALUES({2})".format(table,','.join(list(map(get_only_name,column))),','.join(['?']*len(column)))
		exedata = list()
		for key in list(map(get_only_name,column)):
			try:
				exedata.append(data[key])
			except KeyError:
				return False
		cursor.execute(execomand,exedata)
	except sqlite3.IntegrityError:
		return False
	except Exception as err:
		print("DB insert error",type(err),data,column)
		traceback.print_exc()
		return False
	else:
		return True

def get_only_name(txt):	#"名前 型"の形から名前だけを取り出す関数
	return txt.split(' ')[0]

def create_tables(schema,unique,cursor):
	for key in schema:
		try:
			if(len(unique[key]) == 0):
				cursor.execute("CREATE TABLE {0}({1})".format(key,','.join(schema[key])))
			else:
				cursor.execute("CREATE TABLE {0}({1},unique({2}))".format(key,','.join(schema[key]),','.join(unique[key])))
		except sqlite3.OperationalError:
			#traceback.print_exc()
			print('table {0} was not created'.format(key))
		else:
			print('table {0} was created'.format(key))

def delete_data(table,conditions,cursor):
	try:
		execommand = 'DELETE FROM {0}'.format(table)
		execommand += "" if len(conditions) == 0 else " WHERE "
		execommand += ' and '.join(conditions)
		cursor.execute(execommand)
	except:
		print("sippai")

def write_data_to_csv(data,colum,path):
	if(data["dataType"] in colum):
		filename = datetime.strptime(data["time"],"%Y-%m-%d %H:%M:%S").strftime(path)
		filename = filename.replace("T",data["dataType"])
		dirname = '/'.join(filename.split('/')[:-1])
		os.makedirs(dirname,exist_ok=True)
		if not (os.path.isfile(filename)):
			with open(filename,'w') as f:
				f.write(','.join(colum[data["dataType"]]) + '\n')
		with open(filename,'a') as f:
			writedata = list()
			for dname in colum[data["dataType"]]:
				writedata.append(str(data[dname]))
			f.write(','.join(writedata) + '\n')
	else:
		print(data,'was not inserted in csv')
	#csvに書き込む処理追加

class sqlite_command:
	def __init__(self,command,conditions=[],setdata=None):
		self.data = list()
		self.setdata = setdata
		self.command = command
		self.command += "" if (conditions == []) else " WHERE " + " and ".join(conditions)
		self.finished = threading.Event()

	def execute(self,cursor,tables):
		try:
			if not self.setdata:
				cursor.execute(self.command)
				self.data = cursor.fetchall()
			else:
				for elem in self.setdata:
					cursor.execute(self.command,elem)
		except:
			error_print = traceback.format_exc()
			print(error_print)
			self.data = [error_print]
			return error_print
		finally:
			#print("finished execute sqlite command : {0}".format(self.command))
			self.finished.set()
			if self.setdata != None:
				self.data = "nice"
		return None


class DataBase(threading.Thread):
	def __init__(self,fevent,qdict,parameters):
		#パラメータの初期化
		self.csv_settings = parameters["csv"]
		self.sqlite_settings = parameters["sqlite"]
		self.wait_time = parameters["wait_time"]
		self.fevent = fevent
		self.queues = qdict
		os.makedirs('/'.join(self.sqlite_settings["path"].split("/")[:-1]),exist_ok=True)

		#DBのコネクション作成
		if(self.sqlite_settings["active"]):
			self.tables = self.sqlite_settings["tables"]
			self.uniques = self.sqlite_settings["uniques"]
			con = sqlite3.connect(self.sqlite_settings["path"],isolation_level=None)
			cursor = con.cursor()
			create_tables(self.tables,self.uniques,cursor)
			con.commit()
			con.close()

		threading.Thread.__init__(self,name="DB thread")

	def run(self):
		print('DB Thread RUNNING START')
		self.queues["data"].put({"time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"dataType":"log","importance":"notice","title":"start","body1":"started DB thread","thread":"DB"})
		self.con = sqlite3.connect(self.sqlite_settings["path"],isolation_level=None)
		self.cursor = self.con.cursor()
		dt_before = datetime.now()
		waittime = 0
		is_analyzed = False
		while not self.fevent.wait(timeout=waittime):
			b = time.time()
			
#lineからの受信データを保存
			write_q_append_list = list()
			while not self.queues['data'].empty():
				try:
					elem = self.queues['data'].get()
					if(self.sqlite_settings["active"]):
						write_data_to_sqlite(elem,elem["dataType"],self.tables[elem["dataType"]],self.cursor)
					if(self.csv_settings["active"]):
						write_data_to_csv(elem,self.csv_settings["types"],self.csv_settings["path"])
				except Exception as err:
					traceback.print_exc()
					self.queues["data"].put({"time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"dataType":"log","importance":"danger","title":str(type(err)),"body1":traceback.format_exc(),"thread":"DB"})
				self.con.commit()


#requestの処理
			while not self.queues["request"].empty():
				elem = self.queues["request"].get()
				print("request was" + elem.command)
				self.queues["data"].put({"time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"dataType":"log","importance":"notice","title":"execute command","body1":elem.command,"thread":"DB"})
				err = elem.execute(self.cursor,self.tables)
				self.con.commit()
				if(err):
					self.queues["data"].put({"time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"dataType":"log","importance":"warning","title":'error',"body1":err,"thread":"DB"})
			dt_now = datetime.now()

			if dt_now.hour == dt_before.hour:
				dt_before = dt_now
			else:
				#one time job for one hour.
				if self.sqlite_settings["active"] and self.sqlite_settings["delete"]["active"]:
					for t in self.sqlite_settings["tables"]:
						if(t == "log"):
							continue
						delete_data(t,["datetime(time) < datetime(\'{0}\')".format((dt_now - timedelta(hours=self.sqlite_settings["delete"]["hours"])).strftime("%Y-%m-%d %H:%M:%S")),"is_read = 2"],self.cursor)
			#self.queues["data"].put({"time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"dataType":"log","importance":"update","title":"DB update","body1":"update","thread":"DB"})
			waittime = self.wait_time - time.time() + b
			waittime = waittime if waittime > 0 else 0