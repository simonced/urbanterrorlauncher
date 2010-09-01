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
import subprocess
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
		self.win.servers_tree.get_model().clear()
		self.win.players_tree.get_model().clear()
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
		self.win.servers_tree.get_model().append( list_ )
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
			#and the server status in the list linked by address
			self.win.servers[address] = {"name":utsq_cli.status['sv_hostname'], \
				"map":utsq_cli.status['mapname'], \
				"type":type}
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
			server_raw = "OFFLINE"
			map_name = "OFFLINE"
			bgcolor=UTCFG.DEFAULT_BG_COLOR
			buddy_markup = UTCT.console_colors_to_markup(buddy_raw)
			server_markup = UTCT.console_colors_to_markup(server_raw)
			
			#defaut offline picto
			picto = UTCFG.BUDDY_OFF_ICO
			for server in self.win.players:
				server_players_str = "/".join(self.win.players[server])
				if re.search(re.escape(buddy_raw), server_players_str ):
					picto = UTCFG.BUDDY_ON_ICO
					
					#adapting the already prepared data to match the online status
					server_raw = self.win.servers[server]['name']
					map_name = self.win.servers[server]['map']
					bgcolor = UTCFG.GameColors[ self.win.servers[server]['type'] ]
					buddy_markup = "<b>%s</b>" % (buddy_markup, )
					server_markup = UTCT.console_colors_to_markup(server_raw)
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
	
	
#===
#Threading the servers list refresh
#===
class ServerPlay(GlobalThread):

	def __init__(self, win_, launch_cmd, cwd):
		super(ServerPlay, self).__init__()
		#@param win_ is the urt object with gui and other props
		self.win = win_
		self.launch_cmd = launch_cmd
		self.cwd = cwd
		
	
	def run(self):
		
		# -- running part --
		self.win.game_running = True
		self.updateStatusBar("Game running...")
		print "Game command : " + " ".join(self.launch_cmd)
		
		logs = open("logs.txt", "w")
		subprocess.call(self.launch_cmd, cwd=self.cwd, stderr=logs)	#blocking call for log output
		logs.close()
		# -- / running part --
		
		# --- win object that are used in the following part ---
		servers_model = self.win.servers_tree.get_model()
		# --- / ---
		
		# --- analysis of logs ---
		logs = open("logs.txt")
		server_connected = []
		for line in logs:
			
			#new server played?
			res = re.search("resolved to (\d+\.\d+\.\d+\.\d+)",line)
			if res:
				server_connected.append(res.groups(1)[0])
			
			#other things to analyse later
			#TODO
			
		#closing and removing logs
		logs.close()
		os.remove("logs.txt")
		# -- / analysis of logs --
		
		# -- Servers analysis part --
		#we count the new entries
		new_servers = 0
		
		#analysis of the played server(s)
		for server in set(server_connected):
			if ':' in server:
				(serv_addr, serv_port) = server.strip().split(':', 1)
			else:
				serv_addr = server
				serv_port = UTCFG.DEFAULT_PORT
				server += ":"+str(UTCFG.DEFAULT_PORT)	#simple change for insertion few lines under
				#only in case the port is not specified, unlikely should not happen

			conn = UTSQ.Utsq(serv_addr, int(serv_port) )
			if conn.request:
				host_name = conn.status['sv_hostname']
			else :
				host_name = "HOST WAS UNREACHABLE AT QUERY TIME"
			conn.close()
			
			
			#we need to check in the model (for each line) if this server address already exists
			already = False
			for line in servers_model:
				current = line[1]
				#let's be sure we have the full address
				if ":" not in current:
					current = current + ":" + str(UTCFG.DEFAULT_PORT)
					
				#then we can check
				if current == server:
					#one server at least corresponds, we can skip then
					already = True
					break
			
			#new server? we add it
			if not already:
				#new line formating
				host_name = UTCOLORS.raw_string( host_name )
				new_line = self.win.buildTxtLine(host_name, server, "AUTO")
				#then, we append it to the list file and refreshServers, piece of cake
				self.win.servers_db.addLine(new_line)
				
				new_servers = new_servers + 1
				
		#last step, refreshServers if needed
		if new_servers>0:
			gobject.idle_add(self.refreshServers)
		#--- / servers analysis part ---
		
		
		
		#we unlock the launch command
		self.win.game_running = False
		self.updateStatusBar("Game closed")
		
	
	#===
	#called from thread, refreshes the server list
	def serversRefresh(self):
		 self.win.refreshServers()
		 return False