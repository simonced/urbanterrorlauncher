#!/usr/bin/python
#=!= coding:UTF-8 =!=

"""
Simonced Urban Terror Launcher
simonced@gmail.com
This is a tool to save your prefered servers you play often on.
"""

__author__="simonced@gmail.com"
__version__="0.8"

DEBUG = False

#gui import - GTK
import pygtk
pygtk.require('2.0')
import gtk
import gobject

#system and re imports
import os, re

#sub tools - URT specific
import UrtLauncherThreads as UTTHREAD
import UrbanTerror_colors_tools as UTCOLORS
import UrtLauncherGui as UTGUI
import FileDB

#this file tiny props
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
		self.players = {}	#empty dict, the key is the server address, then (score, ping, name)
		self.buddies = []	
		self.servers = {}	
		#sample {"127.0.0.1":{"name":"Local server", "map":"ut4_icy5b", "type":"FFA"}}
		
		#file object to manage the servers file
		self.servers_db = FileDB.FileManager(UTCFG.ServersFile)
		self.buddies_db = FileDB.FileManager(UTCFG.BuddiesFile)
		
		self.game_running = False
		
		# === GUI creation starting here ===
		self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
		#self.win.set_border_width(5)
		self.win.connect("destroy", self.quit)
		self.win.set_title("Urban Terror Launcher v"+Version)
		self.win.set_size_request(770, 600)
		win_layer = gtk.VBox()
		self.win.add(win_layer)
		
		#creating tab container
		notebook = gtk.Notebook()
		win_layer.pack_start(notebook, True, True, 0)
		
		self.statusBar = gtk.Statusbar()
		win_layer.pack_start(self.statusBar, False, False, 0)
		
		#The first tab is for the servers
		server_tab = gtk.VBox()
		
		# == Section1 == Listing and launching a server
		
		#model for the view (ListStore)
		servers_list = gtk.ListStore(
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_INT,
			str,
			int,
			int,
			gtk.gdk.Pixbuf)

		# model :
		# 0 name (markup)
		# 1 address
		# 2 type
		# 3 players
		# 4 map
		# 5 color (GUI info)
		# 6 Alias (input from user, not really needed)
		# 7 file line number for edit or deletion
		# 8 raw_name of the server without markup or colors to be sorted in the name column of the treeview
		# 9 ping of the server
		# 10 number of players connected (int for sorting)
		# 11 Buddy online on this server? PixBuf
		
		#display object (TreeView)
		self.servers_tree = gtk.TreeView(servers_list)
		
		#signal on click of a line
		self.servers_tree.connect("cursor-changed", self.serverEdit)
		self.servers_tree.connect("row-activated", self.serverPlay)
		self.servers_tree.connect("key-press-event", self.serverDeleteKey)
		
		#cell to render content
		cell = gtk.CellRendererText()
		#cell to render buddy status
		cell_buddy_status = gtk.CellRendererPixbuf()
		
		#column view
		column_name = gtk.TreeViewColumn('Name', cell, markup=0, cell_background=5)
		column_address = gtk.TreeViewColumn('Address', cell, text=1, cell_background=5)
		column_type = gtk.TreeViewColumn('Type', cell, text=2, cell_background=5)
		column_players = gtk.TreeViewColumn('Players')
		column_ping = gtk.TreeViewColumn('Ping', cell, text=9, cell_background=5)
		column_map = gtk.TreeViewColumn('Map', cell, text=4, cell_background=5)

		column_players.pack_start(cell_buddy_status, expand=False)
		column_players.add_attribute(cell_buddy_status, "pixbuf", 11)
                column_players.add_attribute(cell_buddy_status, "cell-background", 5)
		column_players.pack_start(cell, expand=True)
		column_players.add_attribute(cell, "markup", 3)
		column_players.add_attribute(cell, "cell-background", 5)
		
		#adding the columns to the treeview
		self.servers_tree.append_column(column_name)
		self.servers_tree.append_column(column_address)
		self.servers_tree.append_column(column_type)
		self.servers_tree.append_column(column_players)
		self.servers_tree.append_column(column_ping)
		self.servers_tree.append_column(column_map)

		#columns ihm props
		column_name.set_resizable(True)
		column_name.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
		column_address.set_resizable(True)
		column_address.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
		
		#search ok 
		self.servers_tree.set_search_column(0)	#name search only
		#sort ok
		column_name.set_sort_column_id(8)	#using the raw name of the server for sorting
		column_type.set_sort_column_id(2)
		column_players.set_sort_column_id(10)
		column_ping.set_sort_column_id(9)
		#the number is just an order id, if 2 columns sort have same ideas, the sort will effect both columns
		column_name.clicked()	#column 0 sorted from beginning
		
		column_name.set_min_width(200)		#sizes to make it look better
		column_address.set_min_width(160)		#sizes to make it look better
		
		#we need a servers_scroll pane for the servers_tree!
		servers_scroll = gtk.ScrolledWindow()
		servers_scroll.add(self.servers_tree)
		#last step, adding the servers_tree in the window (maybe adding a servers_scroll window between)
		server_tab.pack_start(servers_scroll, True, True, PaddingDefault)


		#then, few buttons that can act on the table rows
		row_treeBts = gtk.HBox()
		self.del_bt = UTGUI.Button("Delete", "rsc/delete_ico.png")
		self.del_bt.set_sensitive(False)	#disabled button
		self.del_bt.connect("clicked", self.serverDelete)
		row_treeBts.pack_end(self.del_bt, False, False, PaddingDefault)
		
		
		self.play_bt = UTGUI.Button("Play", "rsc/play_ico.png")
		self.play_bt.connect("clicked", self.serverPlay)
		row_treeBts.pack_end(self.play_bt, False, False, PaddingDefault)
		
		self.refresh_bt = UTGUI.Button("Refresh", "rsc/refresh_ico.png")
		self.refresh_bt.connect("clicked", self.serversRefresh)
		row_treeBts.pack_end(self.refresh_bt, False, False, PaddingDefault)
		
		#simple label that indicates how many server displayed
		self.servers_label = gtk.Label("Servers listed")
		row_treeBts.pack_start(self.servers_label, False, False, PaddingDefault)
		
		server_tab.pack_start(row_treeBts, False, False, PaddingDefault)
		
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
		label_address.set_size_request(100, 25)
		row2.pack_start(label_address, False, False, PaddingDefault)
		self.server_address = gtk.Entry()
		row2.pack_end(self.server_address, True, True, PaddingDefault)
		bloc_down_left.pack_start(row2, False, False, PaddingDefault)
		
		row1 = gtk.HBox()
		label_name = gtk.Label("Server Alias")
		label_name.set_alignment(0.9, 0.5)	#lign right
		label_name.set_size_request(100, 25)
		row1.pack_start(label_name, False, False, PaddingDefault)
		self.server_name = gtk.Entry()
		row1.pack_end(self.server_name, True, True, PaddingDefault)
		bloc_down_left.pack_start(row1, False, False, PaddingDefault)		
		
		row3 = gtk.HBox()
		label_types = gtk.Label("Game Type")
		label_types.set_alignment(0.9, 0.5)
		label_types.set_size_request(100, 25)
		row3.pack_start(label_types, False, False, PaddingDefault)
		#preparing the list
		self.game_type = gtk.combo_box_new_text()
		for type in UTCFG.GameTypes:
			self.game_type.append_text(type)
		row3.pack_start(self.game_type, False, False, PaddingDefault)
		bloc_down_left.pack_start(row3, False, False, PaddingDefault)
		
		
		row_add = gtk.HBox()
		bt_add = UTGUI.Button("Save", "rsc/save_ico.png")
		bt_add.connect("clicked", self.serverAdd)
		row_add.pack_end(bt_add, False, False, PaddingDefault)
		bloc_down_left.pack_start(row_add, False, False, PaddingDefault)
		
		#last pan that contains 2 blocks splited in half for server and players
		bloc_down.pack_start(bloc_down_left, False, True, PaddingDefault)
		
		# === section 2 - right part - players ===
		bloc_down_right = gtk.VBox()
		
		# == Section 2 - right part ==
		players_list = gtk.ListStore(\
			str, \
			int, \
			int, \
			str, \
			str,
			gtk.gdk.Pixbuf)
		
		#model :
		# 0 player name
		# 1 player score
		# 2 player ping
		# 3 cell color. always white
		# 4 player name markup
		# 5 buddy status pixbuf
		
		self.players_tree = gtk.TreeView(players_list)
		self.players_tree.connect("cursor-changed", self.playerSelected)
		
		#the columns for the view
		column_player_name = gtk.TreeViewColumn('Name')
		column_player_name.pack_start(cell_buddy_status, expand=False)
		column_player_name.add_attribute(cell_buddy_status, "pixbuf", 5)
		column_player_name.add_attribute(cell_buddy_status, "cell-background", 3)
		column_player_name.pack_start(cell, expand=True)
		column_player_name.add_attribute(cell, "markup", 4)
		column_player_name.add_attribute(cell, "cell-background", 3)
		
		column_player_score = gtk.TreeViewColumn('Score', cell, text=1, cell_background=3)
		column_player_ping = gtk.TreeViewColumn('Ping', cell, text=2, cell_background=3)
		#adding the columns to the treeview
		self.players_tree.append_column(column_player_name)
		self.players_tree.append_column(column_player_score)
		self.players_tree.append_column(column_player_ping)
		#columns ihm props
		column_player_name.set_resizable(True)
		column_player_name.set_min_width(200)
		#search ok (#name and type only)
		self.players_tree.set_search_column(0)	#player name search only
		#sort ok
		column_player_name.set_sort_column_id(0)
		column_player_score.set_sort_column_id(1)
		column_player_ping.set_sort_column_id(2)
		column_player_name.clicked()	#default sort on this column
		#scrolable list
		players_scroll = gtk.ScrolledWindow()
		players_scroll.set_size_request(250, 200)
		players_scroll.add(self.players_tree)
		bloc_down_right.pack_start(players_scroll, True, True, PaddingDefault)
		#button to add a player as buddy
		buddy_add_row = gtk.HBox()
		self.buddy_add_bt = UTGUI.Button("Add player in buddy list", "rsc/buddy_add_ico.png")
		self.buddy_add_bt.connect("clicked", self.buddyAdd)
		self.buddy_add_bt.set_sensitive(False)
		buddy_add_row.pack_end(self.buddy_add_bt, False, False, 0)
		bloc_down_right.pack_start(buddy_add_row, False, False, 0)
		
		# === / section 2 - right part - players ===
		bloc_down.pack_start(bloc_down_right, True, True, PaddingDefault)
		
		#adding the 2 blocs in the window
		server_tab.pack_start(bloc_down, False, False, PaddingDefault)
		
		#adding the server tab to the notebook
		notebook.append_page(server_tab, UTGUI.createServersTabTitle() )
		
		
		#==========================
		# === Section 2 === Buddies
		#==========================
		buddies_tab = gtk.VBox()
		notebook.append_page(buddies_tab, UTGUI.createBuddiesTabTitle() )
		
		buddies_list = gtk.ListStore(
			str,
			str,
			str,
			str,
			str,
			str,
			gtk.gdk.Pixbuf,
			str,
			int)
		#model :
		# 0 buddy name
		# 1 server playing if connected
		# 2 map on the playing server
		# 3 color of the row
		# 4 buddy name markup
		# 5 server name markup
		# 6 icon status
		# 7 server address
		# 8 buddy line in the db file
		
		self.buddies_tree = gtk.TreeView(buddies_list )
		self.buddies_tree.connect("cursor-changed", self.buddySelected )
		self.buddies_tree.connect("row-activated", self.buddyJoin )
		self.buddies_tree.connect("key-press-event", self.buddyDeleteKey )

		buddies_scroll = gtk.ScrolledWindow()
		buddies_scroll.add( self.buddies_tree )
		
		#columns needed
		buddy_status_col = gtk.TreeViewColumn(None, cell_buddy_status, pixbuf=6, cell_background=3)
		buddy_name_col = gtk.TreeViewColumn('Name', cell, markup=4, cell_background=3)
		buddy_server_name = gtk.TreeViewColumn('Server', cell, markup=5, cell_background=3)
		buddy_server_map = gtk.TreeViewColumn('Map', cell, text=2, cell_background=3)
		# once columns are set, adding the columns to the treeview
		self.buddies_tree.append_column(buddy_status_col)
		self.buddies_tree.append_column(buddy_name_col)
		self.buddies_tree.append_column(buddy_server_name)
		self.buddies_tree.append_column(buddy_server_map)
		#size props
		buddy_status_col.set_min_width(32)
		buddy_name_col.set_resizable(True)
		buddy_name_col.set_min_width(200)
		buddy_server_name.set_resizable(True)
		buddy_server_name.set_min_width(200)
		buddy_server_map.set_resizable(True)
		buddy_server_map.set_min_width(200)
		
		#sorting options
		buddy_name_col.set_sort_column_id(0)
		buddy_server_name.set_sort_column_id(1)
		buddy_server_map.set_sort_column_id(2)
		buddy_name_col.clicked()	#we activate the sorting by name by default
		
		#adding the tree to the view
		buddies_tab.pack_start(buddies_scroll, True, True, PaddingDefault)
		
		#then a row of buttons to control the action in the buddy list
		buddy_row = gtk.HBox()
		buddies_tab.pack_start(buddy_row, False, False, PaddingDefault)

		#button to delete a buddy
		self.buddy_delete_bt = UTGUI.Button("Delete", "rsc/delete_ico.png")
		self.buddy_delete_bt.connect("clicked", self.buddyDelete )
		buddy_row.pack_end(self.buddy_delete_bt, False, False, PaddingDefault)

		#button to join a buddy
		self.buddy_join_bt = UTGUI.Button("Join", "rsc/play_ico.png")
		self.buddy_join_bt.connect("clicked", self.buddyJoin )
		buddy_row.pack_end(self.buddy_join_bt, False, False, PaddingDefault)

                #button to search buddies on other servers
		self.buddy_search_bt = UTGUI.Button("Search", "rsc/search_ico.png")
		self.buddy_search_bt.connect("clicked", self.buddySearch )
		buddy_row.pack_end(self.buddy_search_bt, False, False, PaddingDefault)
		
		#la fenetre
		#----------
		self.win.show_all()
		
		gtk.gdk.threads_enter()
		
		#init of the GUI with datas from servers
		self.serversRefresh()
		
		gtk.main()
		gtk.gdk.threads_leave()
		

	#===		
	#on quitte l'appli
	def quit(self, data=None):
		self.win.destroy()
		gtk.main_quit()
		
		#then, the servers file
		self.servers_db.close()
		self.buddies_db.close()
	
	#===
	#simple init function for the input fields
	def init(self):
		self.server_address.set_text("")
		self.server_name.set_text("")
		self.game_type.set_active(-1)
		self.del_bt.set_sensitive(False)
		self.buddy_add_bt.set_sensitive(False)
		self.buddy_join_bt.set_sensitive(False)
		self.buddy_delete_bt.set_sensitive(False)
		
		return True
	
	
	#===
	#the click on the refresh button
	def serversRefresh(self, data=None):
		#clean-up of input fields
		self.init()
		
		t = UTTHREAD.ServersRefresh(self)
		t.start()
		
		
	#===
	# allow to update the buddies list after adding a new buddy
	# Useless to call after serversRefresh() because the thread is still updating player list
	def buddiesRefresh(self, data=None):

		t = UTTHREAD.BuddiesRefresh(self)
		t.start()
	
	
	#===
	#editing a line from the servers_tree view (click)
	def serverEdit(self, tree, path=None, column=None):
		(model, iter) = self.servers_tree.get_selection().get_selected()
		if iter==None:
			print("ERROR RECEIVING THE LINE SELECTED IN THE TREEVIEW")
			return False
			
		address = model.get(iter, 1)[0]
		self.server_address.set_text( address )
		self.server_name.set_text( model.get(iter, 6)[0] )
		
		#full players list
		model_players = self.players_tree.get_model()
		model_players.clear()
		#if this server contains players
		if address in self.players:
			for player in self.players[ address ]:
				(score, ping, name) = player
				name_markup = UTCOLORS.console_colors_to_markup( name )
				#picto for buddies
				picto = None
				if name in self.buddies:
					picto = UTCFG.BUDDY_ON_ICO
					
				model_players.append(
					(name,
					score,
					ping,
					UTCFG.DEFAULT_BG_COLOR,
					name_markup,
					picto)
				)
		
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
	#function to insert the new server in our list
	def serverAdd(self, data_=None):
		
		#input data - game type
		type_choisi=""
		index = self.game_type.get_active()
		if index>=0:
			type_choisi = UTCFG.GameTypes[index]
		#text line to be inserted
		line = self.buildTxtLine(self.server_name.get_text(), self.server_address.get_text(), type_choisi)

		#adding a new server
		ok = self.servers_db.addLine(line)
		
		#we delete the previous line if needed, this delete call also refreshes the Tree model
		if not self.serverDelete(None):
			#we still need to serversRefresh
			self.serversRefresh()
		
		return ok
	
	
	#===
	#deleting a line from the servers_tree view
	def serverDelete(self, data_=None):
		
		(model, iter) = self.servers_tree.get_selection().get_selected()
		if iter==None:
			print("ERROR RECEIVING THE LINE SELECTED IN THE TREEVIEW")
			return False
			
		
		try:
			servers_file_line = model.get(iter, 7)[0]
			self.servers_db.delLine(servers_file_line)
			self.serversRefresh()
			return True
			
		
		except:
			print( "ERROR AT DELETION IN THE FILE" )
			return False
	
	
	#===
	#method to handle the DEL key pressed in the servers tree
	def serverDeleteKey(self, widget_, data_event_):
		
		if data_event_.type==gtk.gdk.KEY_PRESS and gtk.gdk.keyval_name(data_event_.keyval)=='Delete':
			self.serverDelete()
		
		return False	
	
	
	#===
	#deleting a line from the tree view
	def serverPlay(self, tree=None, path=None, column=None, server_addr_=None):
		#we dont allow a new game launch
		if(self.game_running):
			return
		
		#will contain the list of arguments to launch the game
		launch_cmd = [self.UrtExec,]
		
		#This method can be used from other calls (objects)
		#This is the way to specify a server address manually
		if server_addr_ :
			launch_cmd.append( "+connect" )
			launch_cmd.append( server_addr_ )
		
		else:
			(model, iter) = self.servers_tree.get_selection().get_selected()
			
			if iter!=None:
				launch_cmd.append( "+connect" )
				launch_cmd.append( model.get(iter, 1)[0] )
		
		# === LAUNCHING THE GAME ===
		exec_path = os.path.dirname(self.UrtExec)	#let's keep aside the path of the game to launch it
		play_t = UTTHREAD.ServerPlay(self, launch_cmd, exec_path)
		play_t.start()	#launching the thread
		

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
				self.UrtExec=v.strip()
				
		f.close()
		
		return True
	
	
	#===
	#function that allows to add a player as buddy (activates the buddy add button)
	def playerSelected(self, tree, path=None, column=None):
		(model, iter) = self.players_tree.get_selection().get_selected()
		player_name = model.get(iter, 0)[0] # column in model > part of the cell (only one in many cases)

		if iter!=None and player_name not in self.buddies:
			self.buddy_add_bt.set_sensitive(True)
		else:
			self.buddy_add_bt.set_sensitive(False)
	
	
	#===
	#function to add a player in the buddy list
	def buddyAdd(self, data_=None):
		
		(model, iter) = self.players_tree.get_selection().get_selected()
		player_name = model.get(iter, 0)[0]	# column in model > part of the cell (only one in many cases)
		self.buddyAddLine(player_name)
		self.buddiesRefresh()	#The refresh update the playes buddy icons ;)
		
		#we disable the add button to prevent a double player add
		self.buddy_add_bt.set_sensitive(False)
		
	
	#===
	#this function creates a new entry in the buddy list
	#Can be called by a thread
	def buddyAddLine(self, player_name):
		self.statusBar.push(1, "Adding %s in buddy-list" % (player_name, ) )
		new_line = player_name + "\n"
		ok = self.buddies_db.addLine(new_line)
		
		return ok
	
	
	#===
	# a line is selected in the list
	def buddySelected(self, tree, path=None, column=None):
		
		#we can delete a buddy offline
		self.buddy_delete_bt.set_sensitive(True)
		#non active button by default
		self.buddy_join_bt.set_sensitive(False)
		
		(model, iter) = self.buddies_tree.get_selection().get_selected()
		if iter:
			server_address = model.get(iter, 7)[0]
			if server_address:
				self.buddy_join_bt.set_sensitive(True)


	#===
	#function to add a player in the buddy list
	def buddyJoin(self, tree=None, path=None, column=None):
		
		(model, iter) = self.buddies_tree.get_selection().get_selected()
		server_address = model.get(iter, 7)[0]
		
		if server_address:
			self.serverPlay(server_addr_=server_address)


        #===
        #Launches a search of the buddies on all online servers, trough Master Server
        def buddySearch(self, widget_=None, data_=None):

            t = UTTHREAD.BuddiesSearch(self)
            t.start()



	#===
	#method to handle the DEL key pressed in the buddies tree
	def buddyDeleteKey(self, widget_, data_event_):

		if data_event_.type==gtk.gdk.KEY_PRESS and gtk.gdk.keyval_name(data_event_.keyval)=='Delete':
			self.buddyDelete()

		return False


	#===
	#Buddy delete method
	def buddyDelete(self, data_=None):
		(model, iter) = self.buddies_tree.get_selection().get_selected()
		if iter==None:
			print("ERROR RECEIVING THE LINE SELECTED IN THE TREEVIEW")
			return False

		try:
			buddy_file_line = model.get(iter, 8)[0]
			self.buddies_db.delLine(buddy_file_line)
			self.buddiesRefresh()
			return True


		except:
			print( "ERROR AT DELETION IN THE FILE" )
			return False


#main loop
#=========
if __name__=="__main__":
	ur_launcher = Utl()
