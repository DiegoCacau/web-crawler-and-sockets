import socket
from struct import unpack
from urllib.parse import urlparse, urljoin
import sys
import os
import re


# classe para baixar html
class ResquestHTML():
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

		self.client.close()

		return self.html

	def get_data(self):
		response = self.client.recv(1024)

		self.parse_data(response)

		# caso o receba "Transfer-Encoding: chunked", o programa desconsidera o
		# tamanho da página e baixa a tentar baixar até o servidor parar de responder
		if(not self.should_stop and not self.chunked_size):
			if(self.total_size > self.actual_size):
				self.get_data()
		elif(not self.should_stop):
			if(response):
				self.get_data()


	def parse_data(self, response):
		# se for a primeira requisição, é necessário parsear o cabeçalho
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

	def get_host(self):
		return self.target_host









# classe para baixar img
class ResquestIMG():
	def __init__(self, url, path):
		self.header_delimiter = b'\r\n\r\n'
		self.is_first_request = True
		self.headers = {}
		self.img = ""
		self.total_size = 0
		self.actual_size = 0
		self.chunked_size = False
		self.should_stop = False
		
		if("http" in path or "www" in path):
			parsed = urlparse(path)
		else:
			parsed = urlparse(urljoin(url,path))
		self.target_host = parsed.netloc
		self.path = parsed.path

		self.define_socket()

	def define_socket(self):
		target_port = 80
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

		try:
			self.client.connect((self.target_host, target_port))
		except Exception as e:
			print(e)
			print("\n")
			self.should_stop = True

	def get(self):
		if(self.should_stop):
			return b""

		request = "GET %s HTTP/1.1\r\nHost: %s\r\n\r\n" % (self.path, self.target_host)
		self.client.send(request.encode())

		self.get_data()

		self.client.close()

		if(self.should_stop):
			return b""

		return self.img

	def get_data(self):
		response = self.client.recv(1024)

		self.parse_data(response)

		if(self.should_stop):
			return

		if(not self.chunked_size):
			if(self.total_size > self.actual_size):
				self.get_data()
		else:
			if(response):
				self.get_data()


	def parse_data(self, response):
		if(self.is_first_request):
			try:
				index = response.index(self.header_delimiter)
			except:
				self.should_stop = True
				return

			self.parse_headers(response[:index])

			if(self.status != 200):
				print("HTTP estatus diferente de 200")
				print("Valor recebido: ", self.status)
				print("\n")
				self.should_stop = True
				return

			self.img = response[index+4:]

			try:
				self.total_size = int(self.headers["Content-Length"])
			except:
				self.chunked_size = True

			self.actual_size = len(response[index:])

			self.is_first_request = False
		else:
			self.img = self.img + response
			
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
		# print(self.headers)
		# print("\n\n")




















if __name__ == "__main__":

	if(len(sys.argv) < 2):
		print("Número de argumentos incorreto!")
		print("A forma correta de rodar esse script é:")
		print("python trabalho.py url")
		sys.exit()

	try
		# limpa arquivos baixados
		with open('temp.txt') as html:
		    content = html.read()
		    for line in content.split("\n"):
		    	try:
		    		os.remove(line)
		    	except:
		    		pass
	except:
		pass



	url = sys.argv[1]   #'http://www.ic.uff.br/index.php/pt/'
	
	# baixa html
	request = ResquestHTML(url)
	html = request.get()

	# salva html no arquivo
	with open("pagina.html", "w") as file:
		file.write(html)


	# encontra <img> no html
	content = ""
	with open('pagina.html') as html:
	    content = html.read()
	    pat = re.compile (r'<img [^>]*src="([^"]+)', re.IGNORECASE)
	    matches = pat.findall(content)



	temp_names = []
	for img in matches:

		name = os.path.basename(img)
		temp_names.append(name)

		# baixa img
		print("\nBaixando imagem: ", img)

		request2 = ResquestIMG(sys.argv[1], img)
		img_content = request2.get()

		# salva a img em arquivo
		with open(name, 'wb') as file_to_write:
			file_to_write.write(img_content)

		# muda a url da img, no html, para um path local
		content = content.replace(img, name)


	# reescreve o html
	with open("pagina.html", "w") as file:
		file.write(content)

	# atualiza arquivos a serem deletados ao rodar o programa
	with open("temp.txt", "w") as file:
		for name in temp_names:
			file.write(name + "\n")