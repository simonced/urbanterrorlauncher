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
import re

import UrbanTerror_server_query as UTSQ
import UrbanTerror_colors_tools as UTCT


#================================
#global thread function can be put here
class GlobalThread(Thread):
	
	def __init__(self):
		super(GlobalThread, self).__init__()
	
	
	#===
	#Same for the last status bar message
	#HAVE to return FALSE
	#===
	def updateStatusBar(self, msg_):
		self.win.statusBar.push(1, msg_ )
		return False


#===
#Threading the servers list refresh
#===
class ServersRefresh(GlobalThread):

	def __init__(self, win_):
		super(ServersRefresh, self).__init__()
		#@param win_ is the urt object with gui and other props
		self.win = win_
	
	#===
	#executing code of this thread
	#===
	def run(self):
		#if server files not found, we skip the loading process
		if not self.win.servers_db:
			return False

		#we clean the list (already in memory, unlike widgets)
		self.win.servers_list.clear()
		self.win.players = {}	#empty the players list
		
		#then we open the file and fill in the list			
		loop = 0
		lines = self.win.servers_db.getAllLines()
		total_loops = len(lines)
		for line in lines:
			#to keep track of the line number
			loop = loop + 1
			
			#refresh of one line ;)
			data = self.refreshOneLine(line, loop)
			
			#update of the model
			gobject.idle_add(self.updateList, \
				data, \
				loop, \
				total_loops)
			
		
		gobject.idle_add(self.updateStatusBar, "List updated : %i servers listed." % (loop,) )
		
		#refreshing the buddies
		buddy_t = BuddiesRefresh(self.win)
		buddy_t.start()
		buddy_t.join()	#we wait for the buddy thread before exiting
		
		return True
	
	
	#===
	#callback to update the listStore of servers.
	#HAVE to return FALSE
	#===
	def updateList(self, list_, current_loop_, total_loops_):
		self.win.servers_list.append( list_ )
		self.win.statusBar.push(1, "Query of server %s/%s..." % (current_loop_, total_loops_) )
		return False 
	
	
	#===
	#one line refresh, can be used out of the thread in the add process
	#but hanged so still used only here
	#===
	def refreshOneLine(self, line_, loop_):
		(conf_name, address, type) = line_.strip().split("|")
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
			#plus, we need the ping time
			ping = int( str(utsq_cli.ping*1000).split('.')[0][0:3] )
			
			#we save at the same time the list of players online for this address ;)
			self.win.players[address] = utsq_cli.clients
			raw_name = UTCT.raw_string( utsq_cli.status['sv_hostname'] )
			
		else:
			#case we can't query the server
			players = "ERR"
			mapname = "ERR"
			servername = "<i>" + conf_name + "</i>"
			raw_name = UTCT.raw_string( conf_name )
			ping = 999
		
		#closing the socket with the server
		utsq_cli.close()
		
		return (servername, address, type, players, mapname, color, conf_name, loop_, raw_name, ping)


#=====================================================
# Thread that refreshes the buddies in the buddies tab
class BuddiesRefresh(GlobalThread):

	def __init__(self, win_):
		super(BuddiesRefresh, self).__init__()
		#@param win_ is the urt object with gui and other props
		self.win = win_
	
	
	def run(self):
		
		#we clean the buddi list in the window object
		self.win.buddies = []	#same for buddies
		
		#if server files not found, we skip the loading process
		if not self.win.buddies_db:
			return False

		#we clean the list (already in memory, unlike widgets)
		self.win.buddies_list.clear()
		
		#then we open the file and fill in the list			
		loop = 0
		lines = self.win.buddies_db.getAllLines()
		total_loops = len(lines)
		for line in lines:
			#to keep track of the line number
			loop = loop + 1
			
			buddy_raw = line
			server_raw = "Server TODO"
			map_name = "Map TODO"
			bgcolor=UTCFG.DEFAULT_BG_COLOR
			buddy_markup = UTCT.console_colors_to_markup(buddy_raw)
			server_markup = UTCT.console_colors_to_markup(server_raw)
			
			#defaut offline picto
			picto = UTCFG.BUDDY_OFF_ICO
			for server in self.win.players:
				server_players_str = "/".join(self.win.players[server])
				if re.search(re.escape(buddy_raw), server_players_str ):
					picto = UTCFG.BUDDY_ON_ICO
					break
				
			data = (buddy_raw, \
				server_raw, \
				map_name, \
				bgcolor, \
				buddy_markup, \
				server_markup, \
				picto)
			
			#update of the model
			gobject.idle_add(self.updateList, \
				data, \
				loop, \
				total_loops)
			
			
		#end of the list of buddies update process
		gobject.idle_add(self.updateStatusBar, "List updated : %i buddies listed." % (loop,) )
		
		return True
	
	
	#===
	#callback to update the listStore of buddies.
	#HAVE to return FALSE
	#===
	def updateList(self, list_, current_loop_, total_loops_):
		#update of inner memory
		self.win.buddies.append(list_[0])
		
		#update of gui elements
		self.win.buddies_list.append( list_ )
		self.win.statusBar.push(1, "Updating buddy status %s/%s..." % (current_loop_, total_loops_) )
		return False 