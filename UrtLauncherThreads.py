#!/usr/bin/python
#=!= coding:UTF-8 =!=
'''
Simonced Urban Terror Launcher
simonced@gmail.com
This is a tool to be used by UrbanTerrorLauncher.
'''

import gtk
import gobject

#common configuration is here
import UrtLauncherConfig as UTCFG

#threading imports
from threading import Thread
import os

import UrbanTerror_server_query as UTSQ
import UrbanTerror_colors_tools as UTCT

#===
#Attempt of threading the servers list refresh
#===
class ServersRefresh(Thread):

	def __init__(self, win_):
		#@param win_ is the urt object with gui and other props
		
		super(ServersRefresh, self).__init__()
		self.win = win_
	
	#===
	#executing code of this thread
	#===
	def run(self):
		
		#if server files not found, we skip the loading process
		if not os.path.isfile(UTCFG.ServersFile):
			return False

		#we clean the list (already in memory, unlike widgets)
		self.win.servers_list.clear()
		
		self.win.players = {}	#empty the players list
		self.win.playtt.players = {}	#same for the tooltip list
		
		#then we open the file and fill in the list			
		f = open(UTCFG.ServersFile, "r")
		loop = 0
		lines = f.readlines()
		total_loops = len(lines)
		f.close()
		for line in lines:
			(conf_name, address, type) = line.strip().split("|")
			if type in UTCFG.GameColors:
				color = UTCFG.GameColors[type]
			else:
				color = "#FFFFFF"	#simple white color
				
			#connection to request the number of players
			try:
				(address1, port2) = address.split(":")
			except:
				address1 = address
				port2 = UTCFG.DEFAULT_PORT

			#server query for players
			utsq_cli = UTSQ.Utsq(address1, int(port2))
			if utsq_cli.request:
				players = str(len(utsq_cli.clients)) + " / " + str(utsq_cli.status['sv_maxclients'])
				if len(utsq_cli.clients)>0 and len(utsq_cli.clients)<utsq_cli.status['sv_maxclients']:
					players = "<b>" + players + "</b>"
				mapname = utsq_cli.status['mapname']
				servername = UTCT.console_colors_to_markup( utsq_cli.status['sv_hostname'] )
				#we save at the same time the list of players online for this address ;)
				self.win.players[address] = self.win.playtt.players[address] = utsq_cli.clients
				
			else:
				#case we can't query the server
				players = "ERR"
				mapname = "ERR"
				servername = "<i>" + conf_name + "</i>"
			
			utsq_cli.close()
			
			#to keep track of the line number
			loop = loop + 1
			
			#update of the model
			gobject.idle_add(self.updateList, \
				(servername, address, type, players, mapname, color, conf_name, loop), \
				loop, \
				total_loops)
			
		
		gobject.idle_add(self.updateStatusBar, "List updated, %i servers listed." % (loop,) )
		
		return True
	
	
	#===
	#callback to update the listStore.
	#HAVE to return FALSE
	#===
	def updateList(self, list_, current_loop_, total_loops_):
		self.win.servers_list.append( list_ )
		self.win.statusBar.push(1, "Query of server %s/%s..." % (current_loop_, total_loops_) )
		return False 

	#===
	#Same for the last status bar message
	#===
	def updateStatusBar(self, msg_):
		self.win.statusBar.push(1, msg_ )
		return False
