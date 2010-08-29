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


def createBuddiesTabTitle():
	
	buddies_tab_title = gtk.HBox()
	#buddies_tab_title.set_size_request(150, 20)
	buddies_tab_title.pack_start(gtk.image_new_from_file("rsc/buddies_ico.png"), False, False, 2)
	buddies_tab_title.pack_start(gtk.Label("Buddies"), True, True, 2)
	buddies_tab_title.show_all()
	
	return buddies_tab_title



def createServersTabTitle():
	
	buddies_tab_title = gtk.HBox()
	#buddies_tab_title.set_size_request(150, 20)
	buddies_tab_title.pack_start(gtk.image_new_from_file("rsc/servers_ico.png"), False, False, 2)
	buddies_tab_title.pack_start(gtk.Label("Servers"), True, True, 2)
	buddies_tab_title.show_all()
	
	return buddies_tab_title