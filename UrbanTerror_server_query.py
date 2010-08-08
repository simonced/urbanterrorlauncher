#!/usr/bin/python
#=!= coding:UTF-8 =!=

"""
Simonced Urban Terror Launcher
simonced@gmail.com
v0.2
This tools is a tool to request the q3 like servers about their status online (map, players...)
"""

import socket

class Utsq:
	
	
	#Constructeur
	def __init__(self, host, port):
		
		self.data = ""	#brute data received from the server
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	#connection udp		
		self.status = {}	#empty dict that will contain the server status response
		self.clients = []
		self.connected = False
		self.request = False	#allow client to know if the send request passed or failed
		self.host = host
		self.port = port
		
		try:
			self.sock.connect( (host, port) )
			self.connected = True
			self.sock.settimeout(1.0)  # timeout of 1 second
			self.getall()
			
		except socket.error:
			print "Error at connexio with %s:%s\n" % (host, port)

	
	#==
	#sending many kind of messages
	def send(self, cmd_):
		data = False

		if self.connected==False:
			return False

		try:
			self.sock.send("\xFF\xFF\xFF\xFF"+cmd_+"\n")
			content = self.sock.recv(65565)
			data = content.strip().split("\n")	# part0 : headers, part1 : status, part2 players
		except:
			print self.host + "SENDING REQUEST STATUS TO SERVER FAILED"
		
		
		return data
	

	#==
	#This function checks everything
	def getall(self):
		
		data = self.send("getstatus")
		
		if data==False:
			self.request = False
			return False
			
		#we can also split the pairs key : value into a dict for easy access
		elems = data[1].split('\\')
		for index in range(len(elems)/2):
			index2 = (index)*2+1	#every 2 elements and wwe skip the first that is always empty
			key = elems[index2].strip()
			val = elems[index2+1].strip()
			self.status[key] = val
		
		#we can also split the pairs key : value into a dict for easy access
		for pi in range(len(data[2:])):
			player = data[pi+2]
			self.clients.append(player)
		
		self.request = True
		return True
	
	
	#===
	#debug script to check data receives
	def debug(self):
		print "== Server Status =="
		for k in self.status:
			print k + " = " + self.status[k]

		print "== Clients =="
		for client in self.clients:
			print client
	
	
	#===
	#fermeture de la connxion
	def close(self):
		self.sock.close()
	

#main loop
#=========
if __name__=="__main__":

	#connection	
	test = Utsq("64.156.192.169", 27960)

	
	##simple debug
	test.debug()
	
	test.close()
