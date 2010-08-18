#!/usr/bin/python
#=!= coding:UTF-8 =!=
'''
Simonced Urban Terror Launcher
simonced@gmail.com
This is a tool to be used by UrbanTErrorLauncher.
'''

#threading imports
from threading import Thread
import time


#===
#Attempt of threading the servers list refresh
#===
class ServersRefresh(Thread):

	def __init__(self, win_):
		#@param win_ is the urt object with gui and other props
		
		super(ServersRefresh, self).__init__()
		self.win = win_
		self.quit = False
	
	
	def run(self):
		
		ok = self.win.loadFile()
		
		self.win.statusBar.push(1, "List updated")
		
		return ok
	
