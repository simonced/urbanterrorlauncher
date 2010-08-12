# Simple lib to convert console colors from URT into HTML codes

__author__="Simonced@gmail.com"
__date__ ="$Aug 11, 2010 12:13:58 PM$"


URT_COLORS = ('black', 'red', 'green', 'yellow', 'blue', 'cyan', 'magenta', 'white')

import pygtk
pygtk.require('2.0')
import gtk
import os
import re


#===
# function to convert the console type colors into markup
def console_colors_to_markup(console_txt_):
	result = ""	#final result to be returned

	parts = re.split("(\^\d.*?)", console_txt_)
	
	replace = False	#we only replace if we encountered a key
	for part in parts:
		#replace from the previous find?
		if replace != False:
			result += "<span color='%s'>%s</span>" % (URT_COLORS[replace], part)
			replace = False
			continue
			
		color_found = re.match("\^(\d)$", part)
		if color_found:
			replace = int( color_found.groups()[0] )
		else:
			result += part
			replace = False

	return result


if __name__ == "__main__":
	#sample server name
	sample = "^1test ^2with ^5colors <b>Woot</b>"
	#sample converted into markup
	sample_markup = console_colors_to_markup( sample )
	print sample_markup

	
	win = gtk.Window(gtk.WINDOW_TOPLEVEL)
	win.set_border_width(5)
	win.set_size_request(300, 100)
	win.connect("destroy", gtk.main_quit )
	win.set_title("Urban Terror Colors Tools Test")

	lbl = gtk.Label()
	lbl.set_property("use-markup", True)
	lbl.set_property("label", sample_markup)
	win.add( lbl )
	win.show_all()
	gtk.main()
