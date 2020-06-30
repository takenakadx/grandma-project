from http.server import SimpleHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse,parse_qs
from lib.Line_api import send_text_messages_to
import lib.DataBase as DBLib
import time
import json
from datetime import datetime

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
	def __init__(self,request,client_address,server,queues,*args):
		self.queues = queues
		self.args = args
		super().__init__(request,client_address,server)

	def do_GET(self):
		parsed_path = urlparse(self.path)
		if(parsed_path.path.endswith('getdata')):
			self.send_response(200)
			self.send_header('Content-type','application/json')
			self.send_header('Aceess-Control-Allow-Origin','*')
			self.end_headers()
			param = parse_qs(parsed_path.query)
			condi = list()
			if ('start' in param):
				condi.append('datetime(time) > datetime(\'{0}\')'.format(datetime.strptime('{:0<14}'.format(param["start"][0]),"%Y%m%d%H%M%S").strftime('%Y-%m-%d %H:%M:%S')))
			if ('end' in param):
				condi.append('datetime(time) < datetime(\'{0}\')'.format(datetime.strptime('{:0<14}'.format(param["end"][0]),"%Y%m%d%H%M%S").strftime('%Y-%m-%d %H:%M:%S')))
			if ('userId' in param):
				condi.append('userId == \'{0}\''.format(param['userId'][0]))
			if ('is_read' in param):
				condi.append('is_read == {}'.format(param['is_read'][0]))
			if not ("type" in param):
				return
			
			data = DBLib.sqlite_command("SELECT * FROM {0}".format(param["type"][0]),conditions=condi)
			self.queues['request'].put(data)
			while not data.finished.is_set():
				time.sleep(1)
			
			self.wfile.write(json.dumps(data.data).encode('utf-8'))
		elif(parsed_path.path.endswith("say")):
			param = parse_qs(parsed_path.query)
			if('text' in param):
				self.queues['voice'].put(param['text'][0])
				self.send_response(200)
				self.send_header('Content-type','text/plain')
				self.end_headers()
			else:
				self.send_error(500)
		elif(parsed_path.path.endswith("update_read")):
			param = parse_qs(parsed_path.query)
			if('datetime' in param) and ('message' in param) and ('userid' in param) and ('to' in param):
				condi = list() 
				condi.append('time = \'{0}\''.format(param["datetime"][0]))
				condi.append('message = \'{0}\''.format(param["message"][0]))
				condi.append('userId = \'{0}\''.format(param["userid"][0]))
				data = DBLib.sqlite_command("UPDATE message SET is_read = {0}".format(param["to"][0]),conditions=condi)
				self.queues['request'].put(data)
				self.send_response(200)
				self.send_header('Content-type','text/plain')
				self.end_headers()
			else:
				self.send_error(500)
		elif(parsed_path.path.endswith("send_message")):
			param = parse_qs(parsed_path.query)
			if('to' in param) and ('message' in param):
				res = send_text_messages_to(param['to'][0],[param['message'][0]])
				self.send_response(res.status_code)
				self.send_header('Content-type','text/plain')
				self.end_headers()
				self.wfile.write(res.text.encode('utf-8'))
		#elif(parsed_path.path.endswith("/")):
		#	self.send_error(404)
		else:
			SimpleHTTPRequestHandler.do_GET(self)

	def do_POST(self):
		parsed_path = urlparse(self.path)
		if(parsed_path.path.endswith("setdata")):
			content_len = int(self.headers["Content-Length"])
			posted_body = self.rfile.read(content_len).decode("utf-8").split(";")
			self.send_response(200)
			self.send_header("Content-type","text/plain")
			self.send_header("Aceess-Control-Allow-Origin","*")
			self.end_headers()
			param = parse_qs(parsed_path.query)
			putdata = list()
			for elem in posted_body:
				putdata.append(elem.split(","))
			injection = ','.join(["?"] * (param["schema"][0].count(",") + 1))
			sqlcommand = DBLib.sqlite_command("INSERT INTO {0}({1}) VALUES({2})".format(param["type"][0],param["schema"][0],injection),setdata=putdata)
			self.queues["request"].put(sqlcommand)
			while not sqlcommand.finished.is_set():
				time.sleep(1)
			self.wfile.write(sqlcommand.data.encode("utf-8"))
		else:
			self.send_error(404)


class python_web_server(ThreadingMixIn, HTTPServer):
	daemon_threads = True
	def __init__(self,server_address,RequestHandlerClass,queue,*args):
		self.queue = queue
		self.args = args
		super().__init__(server_address,RequestHandlerClass)
	def finish_request(self,request,client_address):
		self.RequestHandlerClass(request,client_address,self,self.queue,*self.args)
	"""Handle requests in a separete thread."""


if __name__ == '__main__':
	testserver = python_web_server(('localhost',7777),MyHTTPRequestHandler,"THIS IS TEST SERVER!!")
	try:
		print("server started at localhost:7777")
		testserver.serve_forever()
	except KeyboardInterrupt:
		testserver.close()
		print("server was closed")
