#!/usr/bin/python
#=!= coding:UTF-8 =!=

"""
Simonced Urban Terror Launcher
simonced@gmail.com
Thgis is a tool to save your prefered servers you play often on.
"""
import shlex

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import os
import subprocess, shlex
import UrbanTerror_server_query as UTSQ
from TreeViewTooltips import TreeViewTooltips	#great tooltips lib


Version = "0.6.2"
PaddingDefault = 5
GameTypes = ('FFA', 'TDM', 'TS', 'CTF', 'BOMB', 'ICY')
GameColors = {'FFA':'#fffde0', 'TDM':'#ffd28f', 'TS':'#9effa1', 'CTF':'#ffb0fc', 'BOMB':'#ff8f8f', 'ICY':'#AAAAFF'}

ServersFile = "UrbanTerror_launcher.txt"
DEFAULT_PORT = 27960

#the path to the exec file of the game, overrides the default setting bellow
UrtExec = "/home/jeux/UrbanTerror/1-ut-play.sh"
ConfigFile = "UrbanTerror_launcher.cfg"


#================
# we generalise the great class TreeViewTooltips
#================
class PlayersToolTips(TreeViewTooltips):

	#Constructor
	def __init__(self, players_):
		#we get a link to the players we'll display in the tooltip
		self.players = players_
		
		TreeViewTooltips.__init__(self)
		self.label.set_use_markup(False)	#to prevent wrong parsing from players names


	# 2. overriding get_tooltip()
	def get_tooltip(self, view_, column_, path_):
		tooltip = ""
		
		try:
			address = view_.get_model()[path_[0]][1]
			loop = 0
			for player in self.players[address]:
				tooltip += player.split('"')[1] + "\n"
				loop += 1
				if loop>=6:
					tooltip += "..."
					break
		except:
			tooltip += "SERVER UNREACHABLE\n"		
			
		return tooltip
    
    

#================
# The GUI
#================
class Utl:
	
	#Constructeur
	def __init__(self):
		
		#default values, can be changed by the config
		self.UrtExec = UrtExec
		
		self.loadCfg()

		#basic vars used in the GUI
		self.players = {}	#empty dict, the first key is the server address, then a list of players

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
			gobject.TYPE_STRING)
		#model :
		# name
		# address
		# players
		# map
		# color (GUI info)

		#inserting the data from the file
		self.loadFile(False)
		#display object (TreeView)
		self.tree = gtk.TreeView(self.servers_list)

		#cell to render content
		cell = gtk.CellRendererText()

		#column view
		column_name = gtk.TreeViewColumn('Name', cell, text=0, background=5)
		column_address = gtk.TreeViewColumn('Address', cell, text=1, background=5)
		column_type = gtk.TreeViewColumn('Type', cell, text=2, background=5)
		column_players = gtk.TreeViewColumn('Players', cell, text=3, background=5)
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
		playtt = PlayersToolTips(self.players)
		playtt.add_view(self.tree)
				
		
		#we need a scroll pane for the tree!
		scroll = gtk.ScrolledWindow()
		scroll.add(self.tree)
		#last step, adding the tree in the window (maybe adding a scroll window between)
		layer.pack_start(scroll, True, True, PaddingDefault)


		#then, few buttons that can act on the table rows
		row_treeBts = gtk.HBox()
		self.del_bt = gtk.Button("Delete")
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
		self.server_address.connect("focus-out-event", self.getServerName)
		row2.pack_start(self.server_address, True, True, PaddingDefault)
		bloc_down_left.pack_start(row2, False, False, PaddingDefault)

		row1 = gtk.HBox()
		label_name = gtk.Label("Server Name")		
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
		for type in GameTypes:
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
		gtk.main()
	

	#===		
	#on quitte l'appli
	def quitter(self, data=None):
		self.win.destroy()
		gtk.main_quit()

	#===
	#Simple function to query a server'name from its IP
	def getServerName(self, event_, data_=None):
		address_ = self.server_address.get_text()
		(address, port) = address_.split(":")[0:2]
		if not port:
			port = DEFAULT_PORT
		server = UTSQ.Utsq(address, int(port) )
		self.server_name.set_text(server.status['sv_hostname'])
		

	#===
	#function to insert the new server in our list
	def add(self, data=None):
		
		#les donnees saisies - le type de jeu
		type_choisi=""
		index = self.game_type.get_active()
		if index>=0:
			type_choisi = GameTypes[index]
		#text line to be instered
		line = self.buildTxtLine(self.server_name.get_text(), self.server_address.get_text(), type_choisi)
		
		try:
			file = open(ServersFile, "a")	#append mode
			file.write(line)
			file.close()

			self.loadFile()

		except:
			print("ERROR WHILE SAUVING THE FILE")


	#===
	#the click on the refresh button
	def refresh(self, data=None):
		self.statusBar.push(1, "Refreshing the servers list, please wait...")
		self.win.queue_draw()
		#How to refresh this damn status bar?
		self.loadFile()
		
	
	#===
	#loading the content of the file with the servers inside
	# @param file_ the file to load
	# @param init_ to clean the input fields or not?
	def loadFile(self, init_=True):
		#are we asked to clean the input fields?
		if init_:
			#once loaded, we clean the input fields
			self.server_name.set_text("")
			self.server_address.set_text("")
			self.game_type.set_active(-1)
						
		if not os.path.isfile(ServersFile):
			return False

		#we clean the list
		self.servers_list.clear()
		
			
		#then we open the file and fill in the list			
		f = open(ServersFile, "r")
		for line in f:
			(name, address, type) = line.strip().split("|")
			color = GameColors[type]
			#connextion to request the number of players
			try:
				(address1, port2) = address.split(":")
			except:
				address1 = address
				port2=DEFAULT_PORT
			
			utsq_cli = UTSQ.Utsq(address1, int(port2))
			if utsq_cli.request:
				players = str(len(utsq_cli.clients)) + " / " + str(utsq_cli.status['sv_maxclients'])
				mapname = utsq_cli.status['mapname']
				#we save at the same time the list of players online for this address ;)
				self.players[address] = utsq_cli.clients
			else:
				players = "ERR"
				mapname = ""
			
			#update of the model
			self.servers_list.append( (name, address, type, players, mapname, color ) )

			utsq_cli.close()

		f.close()
	
		if init_:
			self.statusBar.push(1, "Servers list updated")
	

	#===
	#editing a line from the tree view
	def edit(self, tree, path=None, column=None):
		(model, iter) = self.tree.get_selection().get_selected()
		if iter==None:
			print("ERROR RECEIVING THE LINE SELECTED IN THE TREEVIEW")
			return False
			
		self.server_name.set_text( model.get(iter, 0)[0] )
		address = model.get(iter, 1)[0]
		self.server_address.set_text( address )
		
		#full players list
		model_players = self.players_tree.get_model()
		model_players.clear()
		if address in self.players:
			for player in self.players[ address ]:
				(score_full, name ) = player.split('"')[0:2]
				(score, ping) = score_full.split(' ')[0:2]
				model_players.append( (name, int(score.strip()), int(ping.strip()), '#FFFFFF') )

		
		#loop for game types
		loop = 0
		index = -1
		for type in GameTypes:
			if type == model.get(iter, 2)[0].strip():
				index = loop
				break
			loop += 1
		self.game_type.set_active( index )
		
		return False
		

	#===
	#deleting a line from the tree view
	def delete(self, tree):
		(model, iter) = self.tree.get_selection().get_selected()
		if iter==None:
			print("ERROR RECEIVING THE LINE SELECTED IN THE TREEVIEW")
			return False
			
		server_name = model.get(iter, 0)[0]
		server_address = model.get(iter, 1)[0]
		game_type = model.get(iter, 2)[0]

		full_line = self.buildTxtLine(server_name, server_address, game_type)
		try:
			new_file = ""
			f = open(ServersFile, "r")
			for line in f:
				if line != full_line:
					new_file += line
			f.close()

			#opening in write only, to replace all the content
			f = open(ServersFile, "w")
			f.write(new_file)
			f.close()

			return self.loadFile(ServersFile)

		except:
			print( "ERROR AT DELETION IN THE FILE" )
			return False


	#===
	#deleting a line from the tree view
	def play(self, tree, path=None, column=None):
		(model, iter) = self.tree.get_selection().get_selected()
		if iter!=None:
			launch_cmd = self.urtExec + " +connect " + model.get(iter, 1)[0]
			print("launching game with command : " + launch_cmd)
			#os.system(launch_cmd)
			args = shlex.split(launch_cmd)
			subprocess.Popen(args)
			return True
		else:
			print("ERROR RECEIVING THE LINE SELECTED IN THE TREEVIEW")
			return False


	#===
	#Function that creates a line to be inserted into the file	
	def buildTxtLine(self, name, address, type):
		return name.strip() + "|" + address.strip() + "|" + type.strip() + "\n"
		
	
	#===
	#Function to load the config and replace the default values
	def loadCfg(self):
		#config file exists?
		if not os.path.isfile(ConfigFile):
			return False
		#TODO create a default file that the user can change later
		
		f = open(ConfigFile)
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
