import socket
from struct import unpack
from urllib.parse import urlparse
import sys


class Resquest():
	def __init__(self, url):
		self.header_delimiter = b'\r\n\r\n'
		self.end_site_delimiter = "\r\n0\r\n"
		self.is_first_request = True
		self.headers = {}
		self.html = ""
		self.total_size = 0
		self.actual_size = 0
		self.chunked_size = False
		self.should_stop = False
		
		parsed = urlparse(url)
		self.target_host = parsed.netloc
		self.path = parsed.path

		self.define_socket()

	def define_socket(self):
		target_port = 80
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
		self.client.connect((self.target_host,target_port)) 

	def get(self):
		request = "GET %s HTTP/1.1\r\nHost: %s\r\n\r\n" % (self.path, self.target_host)
		self.client.send(request.encode())

		self.get_data()

		return self.html

	def get_data(self):
		response = self.client.recv(1024)

		self.parse_data(response)

		if(not self.should_stop and not self.chunked_size):
			if(self.total_size > self.actual_size):
				self.get_data()
		elif(not self.should_stop):
			if(response):
				self.get_data()


	def parse_data(self, response):
		if(self.is_first_request):
			index = response.index(self.header_delimiter)

			self.parse_headers(response[:index])

			if(self.status != 200):
				print("HTTP estatus diferente de 200")
				print("Valor recebido: ", self.status)
				sys.exit()

			self.html = response[index:].decode("latin-1")

			#######################################
			# para o caso do html vir mal formatado
			# exemplo: http://diegocacau.com/login
			lines = self.html.split("\n")
			count = 0
			for line in lines:
				if("<html" in line.lower() or 
					"html>" in line.lower() or
					"!doctype" in line.lower()):
					break
				else:
					count = count + 1
			self.html = "\n".join(lines[count:])
			#######################################


			try:
				self.total_size = int(self.headers["Content-Length"])
			except:
				self.chunked_size = True

			self.actual_size = len(response[index:])

			self.is_first_request = False
		else:
			# "\r\n0\r\n" está presente como terminação de requisições
			if(self.end_site_delimiter in response.decode("latin-1")):
				self.should_stop = True
				temp = response.decode("latin-1").replace(self.end_site_delimiter, "")
				self.html = self.html + temp
			else:
				self.html = self.html + response.decode("latin-1")
			
			if(not self.chunked_size):
				self.actual_size = self.actual_size + len(response)

	def parse_headers(self, headers):
		data = headers.decode("latin-1")

		status_line = True
		for line in data.split("\r\n"):

			if(status_line):
				self.status = int(line.split(" ")[1])
				status_line = False
				continue
			header_line = line.split(": ")
			self.headers[header_line[0]] = header_line[1]





url = 'http://www.ic.uff.br/index.php/pt/'
request = Resquest(url)
html = request.get()


with open("pagina.html", "w") as file:
	file.write(html)