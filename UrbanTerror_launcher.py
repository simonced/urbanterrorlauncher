#!/usr/bin/python
#=!= coding:UTF-8 =!=

"""
Simonced Urban Terror Launcher
simonced@gmail.com
This is a tool to save your prefered servers you play often on.
"""
__author__="Simonced@gmail.com"
__version__="0.7.2"

#gui import - GTK
import pygtk
pygtk.require('2.0')
import gtk
import gobject

#system and re imports
import os, re
import subprocess, shlex

#sub tools - URT specific
import UrbanTerror_server_query as UTSQ
import UrbanTerror_colors_tools as UTCT
from PlayersTooltips import PlayersToolTips
from UrtLauncherThreads import ServersRefresh


Version = __version__
PaddingDefault = 5
#common configuration is here
import UrtLauncherConfig as UTCFG

#================
# The GUI
#================
class Utl:
	
	#Constructeur
	def __init__(self):
		
		gobject.threads_init()	#threads for GTK
		
		#default values, can be changed by the config
		self.UrtExec = UTCFG.UrtExec
		
		#loading the cfg file that repleaces some values if needed
		self.loadCfg()

		#basic vars used in the GUI
		self.players = {}	#empty dict, the key is the server address, then a list of players

		#GUI creation starting here		
		self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.win.set_border_width(5)
		self.win.connect("destroy", self.quitter)
		self.win.set_title("Urban Terror Launcher v"+Version)
		self.win.set_size_request(750, 600)
		layer = gtk.VBox()
		
		# == Section1 == Listing and launching
		section1_title = gtk.Label("Servers list : ");
		layer.pack_start(section1_title, False, False, PaddingDefault)

		#model for the view (ListStore)
		self.servers_list = gtk.ListStore(\
			gobject.TYPE_STRING, \
			gobject.TYPE_STRING, \
			gobject.TYPE_STRING, \
			gobject.TYPE_STRING, \
			gobject.TYPE_STRING, \
			gobject.TYPE_STRING, \
			gobject.TYPE_STRING, \
			gobject.TYPE_INT)

		# model :
		# 0 name
		# 1 address
		# 2 type
		# 3 players
		# 4 map
		# 5 color (GUI info)
		# 6 Alias (input from user, not really needed)
		# 7 file line number for edit or deletion

		#display object (TreeView)
		self.tree = gtk.TreeView(self.servers_list)

		#cell to render content
		cell = gtk.CellRendererText()

		#column view
		column_name = gtk.TreeViewColumn('Name', cell, markup=0, background=5)
		column_address = gtk.TreeViewColumn('Address', cell, text=1, background=5)
		column_type = gtk.TreeViewColumn('Type', cell, text=2, background=5)
		column_players = gtk.TreeViewColumn('Players', cell, markup=3, background=5)
		column_map = gtk.TreeViewColumn('Map', cell, text=4, background=5)
		
		#adding the columns to the treeview
		self.tree.append_column(column_name)
		self.tree.append_column(column_address)
		self.tree.append_column(column_type)
		self.tree.append_column(column_players)
		self.tree.append_column(column_map)

		#attach to the columns
		column_name.pack_start(cell, True)
		column_address.pack_start(cell, True)
		column_type.pack_start(cell, False)
		column_players.pack_start(cell, False)
		column_map.pack_start(cell, False)
		#text parameter on the column
		column_name.add_attribute(cell, 'text', 0)
		column_address.add_attribute(cell, 'text', 1)
		column_type.add_attribute(cell, 'text', 2)
		column_players.add_attribute(cell, 'text', 3)
		column_map.add_attribute(cell, 'text', 4)
		#columns ihm props
		column_name.set_resizable(True)
		column_name.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
		column_address.set_resizable(True)
		column_address.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
		
		#search ok (#name and type only)
		self.tree.set_search_column(0)	#name search only
		#sort ok
		column_name.set_sort_column_id(0)
		column_type.set_sort_column_id(2)
		column_players.set_sort_column_id(3)
		#the number is just an order id, if 2 columns sort have same ideas, the sort will effect both columns
		column_name.clicked()	#column 0 sorted from beginning

		column_name.set_min_width(200)		#sizes to make it look better
		column_address.set_min_width(200)		#sizes to make it look better
		column_map.set_min_width(180)

		#signal on click of a line
		self.tree.connect("cursor-changed", self.edit)
		self.tree.connect("row-activated", self.play)
		
		#tree tooltips
		self.playtt = PlayersToolTips()
		self.playtt.add_view(self.tree)
		
		
		#we need a scroll pane for the tree!
		scroll = gtk.ScrolledWindow()
		scroll.add(self.tree)
		#last step, adding the tree in the window (maybe adding a scroll window between)
		layer.pack_start(scroll, True, True, PaddingDefault)


		#then, few buttons that can act on the table rows
		row_treeBts = gtk.HBox()
		self.del_bt = gtk.Button("Delete")
		self.del_bt.set_sensitive(False)	#disabled button
		self.del_bt.connect("clicked", self.delete)
		row_treeBts.pack_end(self.del_bt, False, False, PaddingDefault)
		
		
		self.play_bt = gtk.Button("Play")
		self.play_bt.connect("clicked", self.play)
		row_treeBts.pack_end(self.play_bt, False, False, PaddingDefault)
		
		self.refresh_bt = gtk.Button("Refresh")
		self.refresh_bt.connect("clicked", self.refresh)
		row_treeBts.pack_end(self.refresh_bt, False, False, PaddingDefault)
		
		layer.pack_start(row_treeBts, False, False, PaddingDefault)
		
		#Future containers for the bottom part
		bloc_down =  gtk.HBox(True)
		bloc_down_left = gtk.VBox()
		
		# == ==
		# == Section 2 - left part == Insertion of new data
		bloc_down_left.pack_start(gtk.HSeparator(), False, False, PaddingDefault)
		bloc_down_left.pack_start(gtk.Label("Server : "), False, False, PaddingDefault)
		
		
		#Vertical Layer that contains the new entry form
		row2 = gtk.HBox()	
		label_address = gtk.Label("Server Address")
		label_address.set_alignment(0.9, 0.5)
		row2.pack_start(label_address, False, False, PaddingDefault)
		self.server_address = gtk.Entry()
		row2.pack_start(self.server_address, True, True, PaddingDefault)
		bloc_down_left.pack_start(row2, False, False, PaddingDefault)
		
		row1 = gtk.HBox()
		label_name = gtk.Label("Server Alias")
		label_name.set_alignment(0.9, 0.5)	#lign right
		row1.pack_start(label_name, False, False, PaddingDefault)
		self.server_name = gtk.Entry()
		row1.pack_start(self.server_name, True, True, PaddingDefault)
		bloc_down_left.pack_start(row1, False, False, PaddingDefault)		
		
		row3 = gtk.HBox()
		label_types = gtk.Label("Game Type")
		row3.pack_start(label_types, False, False, PaddingDefault)
		#preparing the list
		self.game_type = gtk.combo_box_new_text()
		for type in UTCFG.GameTypes:
			self.game_type.append_text(type)
		row3.pack_start(self.game_type, False, False, PaddingDefault)
		bloc_down_left.pack_start(row3, False, False, PaddingDefault)
		
		
		row_add = gtk.HBox()
		bt_add = gtk.Button("Save")
		bt_add.connect("clicked", self.add )
		row_add.pack_end(bt_add, False, False, PaddingDefault)
		bloc_down_left.pack_start(row_add, False, False, PaddingDefault)
		
		bloc_down.pack_start(bloc_down_left, False, True, PaddingDefault)
		
		# == Section 2 - right part ==
		players_model = gtk.ListStore(\
			gobject.TYPE_STRING, \
			gobject.TYPE_INT, \
			gobject.TYPE_INT, \
			gobject.TYPE_STRING)
		#model :
		# player name
		# player score
		# player ping
		# cell color. always white
		
		self.players_tree = gtk.TreeView(players_model)
		#the columns for the view
		column_player_name = gtk.TreeViewColumn('Name', cell, text=0, background=3)
		column_player_score = gtk.TreeViewColumn('Score', cell, text=1, background=3)
		column_player_ping = gtk.TreeViewColumn('Ping', cell, text=2, background=3)
		#adding the columns to the treeview
		self.players_tree.append_column(column_player_name)
		self.players_tree.append_column(column_player_score)
		self.players_tree.append_column(column_player_ping)
		#attach to the columns
		column_player_name.pack_start(cell, True)	#we use the same cell model than in the previous tree above
		column_player_score.pack_start(cell, False)
		column_player_ping.pack_start(cell, False)
		#cell attributes
		column_player_name.add_attribute(cell, 'text', 0)
		column_player_score.add_attribute(cell, 'text', 1)
		column_player_ping.add_attribute(cell, 'text', 2)
		#columns ihm props
		column_player_name.set_resizable(True)
		column_player_name.set_min_width(200)
		#search ok (#name and type only)
		self.players_tree.set_search_column(0)	#player name search only
		#sort ok
		column_player_name.set_sort_column_id(0)
		column_player_score.set_sort_column_id(1)
		column_player_ping.set_sort_column_id(2)

		players_scroll = gtk.ScrolledWindow()
		players_scroll.add(self.players_tree)
		bloc_down.pack_start(players_scroll, True, True, PaddingDefault)
		
		
		#adding the 2 blocs in the window
		layer.pack_start(bloc_down, False, False, PaddingDefault)
		
		self.statusBar = gtk.Statusbar()
		layer.pack_end(self.statusBar, False, False, PaddingDefault)
		
		#la fenetre
		#----------
		self.win.add(layer)
		self.win.show_all()
		
		gtk.gdk.threads_enter()
		
		#init of the GUI with datas from servers
		self.refresh()
		
		gtk.main()
		gtk.gdk.threads_leave()
		

	#===		
	#on quitte l'appli
	def quitter(self, data=None):
		self.win.destroy()
		gtk.main_quit()


	#===
	#the click on the refresh button
	def refresh(self, data=None):
		#once loaded, we clean the input fields
		self.server_address.set_text("")
		self.server_name.set_text("")
		self.game_type.set_active(-1)
		self.del_bt.set_sensitive(False)

		t = ServersRefresh(self)
		ok = t.start()
		
		return ok
	
	
	#===
	#function to insert the new server in our list
	def add(self, data_=None):
		
		#les donnees saisies - le type de jeu
		type_choisi=""
		index = self.game_type.get_active()
		if index>=0:
			type_choisi = UTCFG.GameTypes[index]
		#text line to be instered
		line = self.buildTxtLine(self.server_name.get_text(), self.server_address.get_text(), type_choisi)

		try:
			file = open(UTCFG.ServersFile, "a")	#append mode
			file.write(line)
			file.close()

		except:
			print("ERROR WHILE SAVING THE FILE")

		#we delete the previous line if needed, this delete call also refreshes the Tree model
		self.delete(None)


	#===
	#editing a line from the tree view
	def edit(self, tree, path=None, column=None):
		(model, iter) = self.tree.get_selection().get_selected()
		if iter==None:
			print("ERROR RECEIVING THE LINE SELECTED IN THE TREEVIEW")
			return False
			
		address = model.get(iter, 1)[0]
		self.server_address.set_text( address )
		self.server_name.set_text( model.get(iter, 6)[0] )

		#full players list
		model_players = self.players_tree.get_model()
		model_players.clear()
		if address in self.players:
			for player in self.players[ address ]:
				(score_full, name ) = player.split('"', 1)
				(score, ping) = score_full.split(' ', 1)
				model_players.append( (name, int(score.strip()), int(ping.strip()), '#FFFFFF') )
		
		#loop for game types
		loop = 0
		index = -1
		for type in UTCFG.GameTypes:
			if type == model.get(iter, 2)[0].strip():
				index = loop
				break
			loop += 1
		self.game_type.set_active( index )

		#then, we can also activate the del button
		self.del_bt.set_sensitive(True)

		return False
		

	#===
	#deleting a line from the tree view
	def delete(self, tree):
		(model, iter) = self.tree.get_selection().get_selected()
		if iter==None:
			print("ERROR RECEIVING THE LINE SELECTED IN THE TREEVIEW")
			return False
			
		servers_file_line = model.get(iter, 7)[0]
		try:
			new_file = ""
			f = open(ServersFile, "r")
			loop = 0
			for line in f:
				if loop != servers_file_line:
					new_file += line
				loop = loop + 1
			f.close()

			#opening in write only, to replace all the content
			f = open(ServersFile, "w")
			f.write(new_file)
			f.close()

			return self.refresh()

		except:
			print( "ERROR AT DELETION IN THE FILE" )
			return False


	#===
	#deleting a line from the tree view
	def play(self, tree, path=None, column=None):
		(model, iter) = self.tree.get_selection().get_selected()
		if iter!=None:
			launch_cmd = self.urtExec + " +connect " + model.get(iter, 1)[0]
		else:
			launch_cmd = self.urtExec
		
		# === LAUNCHING THE GAME ===
		print("launching game with command : " + launch_cmd)
		args = shlex.split(launch_cmd)
		logs = open("logs.txt", "w")
		subprocess.call(args, stderr=logs)
		logs.close()
		
		# === ANALYSIS OF LOGS ===
		logs = open("logs.txt")
		server_connected = []
		#todo : analyse the logs
		for line in logs:
			res = re.search("resolved to (\d+\.\d+\.\d+\.\d+)",line)
			if res:
				server_connected.append(res.groups(1)[0])
		logs.close()
		#no need of logs anymore
		os.remove("logs.txt")
		
		#we count the new entries
		new_servers = 0
		
		#analysis of the played server(s)
		for server in set(server_connected):
			if ':' in server:
				(serv_addr, serv_port) = server.strip().split(':', 1)
			else:
				serv_addr = server
				serv_port = DEFAULT_PORT
				server += ":"+str(DEFAULT_PORT)	#simple change for insertion few lines under
				#only in case the port is not specified, unlikely should not happen

			conn = UTSQ.Utsq(serv_addr, int(serv_port) )
			if conn.request:
				host_name = conn.status['sv_hostname']
			else :
				host_name = "HOST WAS UNREACHABLE AT QUERY TIME"
			conn.close()
			
			
			#we need to check in the model (for each line) if this server address already exists
			already = False
			for line in self.servers_list:
				current = line[1]
				#let's be sure we have the full address
				if ":" not in current:
					current = current + ":" + str(DEFAULT_PORT)
					
				#then we can check
				if current == server:
					#one server at least corresponds, we can skip then
					already = True
					break
			
			#new server? we add it
			if not already:
				#new line format
				new_line = self.buildTxtLine(host_name, server, "AUTO")
				#then, we append it to the list file and refresh, piece of cake
				servers_file = open(UTCFG.ServersFile, "a")
				servers_file.write(new_line)
				servers_file.close()
				
				new_servers = new_servers + 1
				
		#last step, refresh if needed
		if new_servers>0:
			self.refresh()
		
		return True


	#===
	#Function that creates a line to be inserted into the file	
	def buildTxtLine(self, name, address, type):
		name = name.replace("|", "=")	#will do for instance
		return name.strip() + "|" + address.strip() + "|" + type.strip() + "\n"
		
	
	#===
	#Function to load the config and replace the default values
	def loadCfg(self):
		#config file exists?
		if not os.path.isfile(UTCFG.ConfigFile):
			return False
		#TODO create a default file that the user can change later
		
		f = open(UTCFG.ConfigFile)
		for line in f:
			#non data line, we skip
			if "=" not in line:
				continue
			(k, v) = line.split("=")
			#replace the actual default value
			if k=="UrtExec":
				self.urtExec=v.strip()
		f.close()
		
		return True


#main loop
#=========
if __name__=="__main__":
	ur_launcher = Utl()
