#!/usr/bin/python
#=!= coding:UTF-8 =!=
'''
Simonced Urban Terror Launcher
simonced@gmail.com
This is a configuration to be used by UrbanTErrorLauncher.
'''

#gui import - GTK
import pygtk
pygtk.require('2.0')
import gtk

GameTypes = ('FFA', 'TDM', 'TS', 'CTF', 'BOMB', 'ICY')
GameColors = {"FFA":"#FFFCCC", "TDM":"#FFEBCC", "TS":"#FFE7CC", "CTF":"#FFCCFD", "BOMB":"#FFCCCC", "ICY":"#CCFEFF"}

#cell background by default
DEFAULT_BG_COLOR = "#EEEEEE"

#buddy icons
BUDDY_ON_ICO = gtk.gdk.pixbuf_new_from_file("rsc/buddy_ico.png")
BUDDY_OFF_ICO = gtk.gdk.pixbuf_new_from_file("rsc/buddy_off_ico.png")
BUDDY_OUT_ICO = gtk.gdk.pixbuf_new_from_file("rsc/buddy_out_ico.png")

ServersFile = "UrbanTerror_launcher.txt"
BuddiesFile = "UrbanTerror_buddies.txt"
DEFAULT_PORT = 27960

#the path to the exec file of the game, overrides the default setting bellow
UrtExec = "/home/jeux/UrbanTerror/1-ut-play.sh"
ConfigFile = "UrbanTerror_launcher.cfg"