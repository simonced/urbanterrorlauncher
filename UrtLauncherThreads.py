#!/usr/bin/python
#=!= coding:UTF-8 =!=
'''
Simonced Urban Terror Launcher
simonced@gmail.com
This is a tool to be used by UrbanTerrorLauncher.
'''

#import gtk
from UrtLauncherConfig import DEFAULT_PORT
from UrtLauncherConfig import BUDDY_OUT_ICO
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
import UrtLauncherGui as UTGUI


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
        #Method that updates the Buddies Tab title
        #HAVE TO RETURN FALSE
        def updateBuddiesTabTitle(self, online_buddies_count_):
            title_widget = UTGUI.createBuddiesTabTitle(online_buddies_count_)
            self.win.notebook.set_tab_label(self.win.buddies_tab, title_widget)
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
		
		gobject.idle_add(self.updateStatusBar, "Servers list being refreshed...")
		
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
			
		
		gobject.idle_add(self.updateStatusBar, "Servers list updated : %i servers" % (loop,) )

		#refreshing the buddies
		buddy_t = BuddiesRefresh(self.win)
		buddy_t.start()
		buddy_t.join()	#we wait for the buddy thread before exiting
		
		return True
	
	
	#===
	#Gui method to display list status
	def updateStatusBar(self, msg_):
		self.win.servers_label.set_text(msg_)
		GlobalThread.updateStatusBar(self, msg_)
		return False
	
	
	#===
	#callback to update the listStore of servers.
	#HAVE to return FALSE
	#===
	def updateList(self, list_, current_loop_, total_loops_):
		#input data
		self.win.servers_tree.get_model().append( list_ )
		
		#display
		status = "Query of server %s/%s..." % (current_loop_, total_loops_)
		self.win.statusBar.push(1, status)
		
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
		
		#default buddy ico
		buddy_picto = UTCFG.BUDDY_OFF_ICO
		
		#server query for players
		utsq_cli = UTSQ.Utsq(address1, int(port2))
		if utsq_cli.request:
			#players count
			players = str(len(utsq_cli.clients)) + " / " + str(utsq_cli.status['sv_maxclients'])
			players_int = len(utsq_cli.clients)
			
			if len(utsq_cli.clients)>0 and len(utsq_cli.clients)<utsq_cli.status['sv_maxclients']:
				players = "<b>" + players + "</b>"
			mapname = utsq_cli.status['mapname']
			servername = UTCT.console_colors_to_markup( utsq_cli.status['sv_hostname'] )
			#plus, we need the ping time
			ping = int( str(utsq_cli.ping*1000).split('.')[0][0:3] )
			
			#we save at the same time the list of players online for this address ;)
			self.win.players[address]=[]	#new entry as array for this server address
			for player in utsq_cli.clients:
				(score_full, player_name ) = player.split('"')[0:2]
				(player_score, player_ping) = score_full.split(' ', 1)
				#adding the 3 infos concerning players
				self.win.players[address].append( (int(player_score), int(player_ping), player_name) )

			#and the server status in the list linked by address
			self.win.servers[address] = {"name":utsq_cli.status['sv_hostname'], \
				"map":utsq_cli.status['mapname'], \
				"type":type}
			raw_name = UTCT.raw_string( utsq_cli.status['sv_hostname'] )
			
		else:
			#case we can't query the server
			players = "ERR"
			players_int = 0
			mapname = "ERR"
			servername = "<i>" + conf_name + "</i>"
			raw_name = UTCT.raw_string( conf_name )
			ping = 999
		
		#closing the socket with the server
		utsq_cli.close()
		
		return (servername, 
			address, 
			type, 
			players, 
			mapname, 
			color, 
			conf_name, 
			loop_, 
			raw_name, 
			ping, 
			players_int,
			buddy_picto)


#=====================================================
# Thread that refreshes the buddies in the buddies tab
class BuddiesRefresh(GlobalThread):
        
        buddies_online = 0
        server_search_count = 0
        server_search_total = 0

	def __init__(self, win_):
            super(BuddiesRefresh, self).__init__()
            #@param win_ is the urt object with gui and other props
            self.win = win_

	
	def run(self):
            #if server files not found, we skip the loading process
            if not self.win.buddies_db:
                return False

            #we clean the buddi list in the window object
            self.win.buddies = []

            gobject.idle_add(self.updateBuddiesTabTitle, 0)

            #we clean the list (already in memory, unlike widgets)
            self.win.buddies_tree.get_model().clear()

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
                bgcolor = UTCFG.DEFAULT_BG_COLOR
                buddy_markup = UTCT.console_colors_to_markup(buddy_raw)
                server_markup = UTCT.console_colors_to_markup(server_raw)
                picto = UTCFG.BUDDY_OFF_ICO #defaut offline picto
                server_address = ""
                buddy_line = loop


                #ready to update the buddy tree view thru the model
                data = (buddy_raw,
                        server_raw,
                        map_name,
                        bgcolor,
                        buddy_markup,
                        server_markup,
                        picto,
                        server_address,
                        buddy_line)

                #update of the model and inner list
                gobject.idle_add(self.updateList,
                                 data,
                                 loop,
                                 total_loops)

            #seems that some of servers in bookmark are not listed in Master server?
            #we'll querry them now, but we'll exclude them from the Master response
            for server in self.win.servers:
                print "Bookmarked Server Search:" + server
                t_search = BuddiesSearch(self.win, server)
                t_search.start()

            #update of buddies status by searching them online
            BuddiesRefresh.buddies_online = 0
            servers = UTSQ.masterQuery()
            BuddiesRefresh.server_search_count = 0
            BuddiesRefresh.server_search_total = len(servers)
            #we can update the buddies status here now
            for server in servers:
                if server not in self.win.servers:
                    print "Master Server Search:" + server
                    t_search = BuddiesSearch(self.win, server)
                    t_search.start()

            return True
	
	
	#===
	#callback to update the listStore of buddies.
	#HAVE to return FALSE
	#===
	def updateList(self, list_, current_loop_, total_loops_):
		#update of inner memory (only buddy name)
		self.win.buddies.append(list_[0])
		
		#update of gui elements
		self.win.buddies_tree.get_model().append( list_ )
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

                #Trying a new way because seems to have problems to get logs in Windows
                logs = subprocess.Popen(self.launch_cmd, cwd=self.cwd, stdout=subprocess.PIPE).communicate()[0]
		# -- / running part --

		# --- win object that are used in the following part ---
		servers_model = self.win.servers_tree.get_model()
		# --- / ---
		
		# --- analysis of logs ---
		server_connected = []
		for line in logs:
			
			#new server played?
			res = re.search("resolved to (\d+\.\d+\.\d+\.\d+)",line)
			if res:
				server_connected.append(res.groups(1)[0])
			
			#other things to analyse later
			#TODO

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



#===
#Threading the search of buddies in other servers
#===
class BuddiesSearch(GlobalThread):
        
	def __init__(self, win_, server_addr_):
		super(BuddiesSearch, self).__init__()
		#@param win_ is the urt object with gui and other props
		self.win = win_
                self.server_addr = server_addr_
                if self.server_addr.find(":") < 0:
                    self.server_addr+=":" + str(UTCFG.DEFAULT_PORT)


        #===
        #let's serch for players on other servers
        def run(self):

            #query of the server
            addr, port = self.server_addr.split(":")
            serv = UTSQ.Utsq(addr, int(port) )
            #clean players string so search inside
            players_str = ""
            for client in serv.clients:
                players_str += client.split(" ", 2)[2].replace('"', '').strip()+"\n"

            for buddy in self.win.buddies:
                #buddy online? -- JOIN SEARCH
                if players_str.find(buddy) >= 0:
                    print "%s is found on the server : %s" % (buddy, self.server_addr)

                    self.win.buddies_tree.get_model().foreach(self.updateBuddyLine,
                        (UTCT.raw_string(buddy),
                        UTCT.raw_string(serv.status['sv_hostname']),
                        serv.status['mapname'],
                        UTCT.console_colors_to_markup(buddy),
                        UTCT.console_colors_to_markup(serv.status['sv_hostname']),
                        self.server_addr) )
                        # 0 buddy name
                        # 1 server playing if connected
                        # 2 map on the playing server
                        # 4 buddy name markup
                        # 5 server name markup
                        # 7 server address

                    #update of the title
                    BuddiesRefresh.buddies_online += 1
                    gobject.idle_add(self.updateBuddiesTabTitle, BuddiesRefresh.buddies_online)

            #close the server socket
            serv.close()

            BuddiesRefresh.server_search_count += 1
            gobject.idle_add(self.updateStatusBar,
                "Searching for buddies from the Master Server : %i / %i" % (BuddiesRefresh.server_search_count, BuddiesRefresh.server_search_total) )


        #===
        #update of the model of buddies
	def updateBuddyLine(self, tree_, path_, iter_, data_):
            #data_ struct (numbers are index in the model)
            # 0 buddy name
            # 1 server playing if connected
            # 2 map on the playing server
            # 4 buddy name markup
            # 5 server name markup
            # 7 server address
                
            #current buddy found on another server?
            if tree_.get_value(iter_, 0)==data_[0]:

                tree_.set_value(iter_, 1, data_[1])
                tree_.set_value(iter_, 2, data_[2])
                tree_.set_value(iter_, 5, data_[4])
                tree_.set_value(iter_, 7, data_[5])
                
                #specific cases
                if data_[5] in self.win.servers:
                    #buddy on a server in our bookmarks
                    tree_.set_value(iter_, 4, "<b>"+data_[3]+"</b>")
                    tree_.set_value(iter_, 6, UTCFG.BUDDY_ON_ICO)
                    tree_.set_value(iter_, 3, UTCFG.GameColors[ self.win.servers[ data_[5] ]['type'] ])
                    #update of the server tab
                    gobject.idle_add(self.updateServersTab)
                else:
                    #buddy online on another server
                    tree_.set_value(iter_, 6, UTCFG.BUDDY_OUT_ICO)
                


    	#===
	#method to update the servers tab buddy icons
	#HAVE TO RETURN FALSE
	def updateServersTab(self):

		#check for each server
		self.win.servers_tree.get_model().foreach(self.updateServersTabLine)

		#check for each player selected if any
		#the player list is linked to the server address
		(model, paths) = self.win.servers_tree.get_selection().get_selected_rows()
		if paths:
			#only if one server is selected, we display the list of players
			self.win.servers_tree.set_cursor(paths[0])
			#reselect the same line that triggers the event

		return False


	#===
	#update one server line of the tree view
	def updateServersTabLine(self, tree_, path_, iter_, data_=None):
		#reset the icon
		tree_.set_value(iter_, 11, UTCFG.BUDDY_OFF_ICO)

		#the player list is linked to the server address
		address = tree_.get_value(iter_, 1)
		#players on this server?
		if address in self.win.players:
			#we compare each player in the buddy list
			for buddy in self.win.buddies:
				#buddy online? -- JOIN SEARCH
				if "\n".join([player[2] for player in self.win.players[address]]).find(buddy)>=0:
					tree_.set_value(iter_, 11, UTCFG.BUDDY_ON_ICO)
					break


	#===
	#update of one server players data
	def updateServersTabPlayerLine(self, tree_, path_, iter_, data_=None):
		#reset the icon
		tree_.set_value(iter_, 11, UTCFG.BUDDY_OFF_ICO)


		#players on this server?
		if address in self.win.players:
			#we compare each player in the buddy list
			for buddy in self.win.buddies:
				#buddy online?
				if buddy in [player[2] for player in self.win.players[address]]:
					tree_.set_value(iter_, 11, UTCFG.BUDDY_ON_ICO)
					break