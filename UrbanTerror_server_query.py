#!/usr/bin/python
#=!= coding:UTF-8 =!=

"""
Simonced Urban Terror Launcher
simonced@gmail.com
v0.3
This tools is a tool to request the q3 like servers about their status online (map, players...)
"""

import socket
import time

class Utsq:
	
	
	#Constructeur
	def __init__(self, host, port, autoGetAll_=True):
		
		self.data = ""	#brute data received from the server
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	#connection udp		
		self.status = {}	#empty dict that will contain the server status response
		self.clients = []       #raw data of players connected on the server
                
		self.raw_response = ""  #Raw response from the server after sending a query
                self.connected = False
		self.request = False	#allow client to know if the send request passed or failed
		self.host = host
		self.port = port
		self.ping = 0	#time the server answers in
		
		try:
			self.sock.connect( (host, port) )
			self.connected = True
			self.sock.settimeout(1.0)  # timeout of 1 second

                        #server queried automatically by default
			if autoGetAll_:
                            self.getServerStatus()
			
			
		except socket.error:
			print "Error at connexio with %s:%s\n" % (host, port)

	
	#===
	#sending many kind of messages
	def send(self, cmd_):
		data = False

		if self.connected==False:
			return False

		try:
			self.sock.send("\xFF\xFF\xFF\xFF"+cmd_+"\n")
			#patch to get the ping value
			start = time.time()
                        #receiving data
                        content = self.sock.recv(65565)
                        self.ping = time.time() - start

                        #we keep track of the total answer
                        self.raw_response = content.strip()
                        #we split headers and data
                        data = self.raw_response.split("\n")	# part0 : headers, part1 : status, part2 players
                        
		except:
			print self.host + "SENDING %s COMMAND TO SERVER FAILED" % cmd_
		
		return data
	

	#===
	#This function checks everything
	def getServerStatus(self):
		
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
        # Query the Master Server
        def getMasterStatus(self):

            #to get all servers, we can use ; getservers 68 full empty
            #but we dont need empty servers
            self.send("getservers 68 full")
            data = self.raw_response
            answer_expected = "\xFF\xFF\xFF\xFFgetserversResponse\\"

            #TODO ; analysing the received data
            if answer_expected not in data:
                print "ERROR, WRONG ANSWER RECEIVED"
                return False

            #we work on a copy
            data = data.replace(answer_expected, "")
            #split by group of 7 characters
            list = [ data[index*7:(index*7)+7] for index in range(len(data)/7) ]

            servers = []
            for address in list:
                #print address
                parts = [ str(ord(charac)) for charac in address ]
                #print parts
                address_str = ".".join( parts[0:4] )
                address_str += ":" + str(256*ord(address[4]) + ord(address[5]))
                #print address_str
                servers.append(address_str)

            #we finished
            return servers

	
	#===
	#debug script to check data receives
	def debug(self):

                print "== Raw Status =="
                print self.raw_response

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

	""" single server test 
        #connection
	test1 = Utsq("64.156.192.169", 27960)
        #simple debug
	test1.debug()
        test1.close()
        """
        
        """ master server query test """
        print "=== MASTER QUERY ==="
        #connection
	test2 = Utsq("master.urbanterror.net", 27950, False)
        servers = test2.getMasterStatus()
        print servers
        #simple debug
	#test2.debug()
	test2.close()
