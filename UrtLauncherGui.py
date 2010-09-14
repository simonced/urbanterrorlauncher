#!/usr/bin/python
#=!= coding:UTF-8 =!=

"""
Simonced Urban Terror Launcher
simonced@gmail.com
This contains some shortcuts to create a nice GUI
"""
__author__="Simonced@gmail.com"


#gui import - GTK
import pygtk
pygtk.require('2.0')
import gtk
import gobject

import os


def createBuddiesTabTitle(num_=0):
	
	buddies_tab_title = gtk.HBox()
	#buddies_tab_title.set_size_request(150, 20)
	buddies_tab_title.pack_start(gtk.image_new_from_file("rsc/buddies_ico.png"), False, False, 2)
	buddies_tab_title.pack_start(gtk.Label("Buddies (%i)" % num_), True, True, 2)
	buddies_tab_title.show_all()
	
	return buddies_tab_title



def createServersTabTitle():
	
	buddies_tab_title = gtk.HBox()
	#buddies_tab_title.set_size_request(150, 20)
	buddies_tab_title.pack_start(gtk.image_new_from_file("rsc/servers_ico.png"), False, False, 2)
	buddies_tab_title.pack_start(gtk.Label("Servers"), True, True, 2)
	buddies_tab_title.show_all()
	
	return buddies_tab_title


#my own button to display an icon next to it even in pygtk 2.0
class Button(gtk.Button):
	
	#My Button constructor
	def __init__(self, label_, image_path_=None):
		#parent constructor
		super(Button, self).__init__()
		
		#container
		cont = gtk.HBox()
		
		#image available?
		if os.path.exists(image_path_):
			cont.pack_start( gtk.image_new_from_file(image_path_), False, False, 0 )
			
		#Label
		cont.pack_start( gtk.Label(label_), True, True, 5 )
		
		#We add everything in our button
		self.add(cont)
	