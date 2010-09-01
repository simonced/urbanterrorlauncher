#!/usr/bin/python
#=!= coding:UTF-8 =!=

"""
Simonced UFile DB tools.
simonced@gmail.com

Simply file handling of formated files
"""

import os


class FileManager:
	
	#===
	#constructor
	def __init__(self, name_):
		
		#memo of the current file
		self.name = name_
		#last line read, 0 means no read yet (start of the file)
		self.read_counter = 0
		
		#pointer of opened file in read mode
		self.file_read = None
		self.file_write = None
		#TODO adding format features like separators and so on
		
		#creation of a default file
		if not os.path.exists(self.name):
			f = open('w')
			f.close()
	
	
	#===
	#close the opened pointers if needed
	def close(self):
		
		print "Closing the file %s" %(self.name, )
		
		if self.file_read:
			self.file_read.close()
			self.file_read = None
			self.read_counter = 0
		
		if self.file_write:
			self.file_write.close()
			self.file_write = None
		
		return 0
	
	#===
	#function to reset the read process
	def reset(self):
		if self.file_read:
			self.file_read.flush()
			self.file_read.seek(0)
			self.read_counter = 0
		
		return True
	
	
	#===
	#simple append method
	def addLine(self, line_):
		
		#TODO : using seek to go to the end of the file and append data.
		#This way, use of only one pointer
		
		try:
			if not self.file_write:
				self.file_write = open(self.name, 'a')	#append mode
			
			self.file_write.write(line_)
			self.file_write.flush()
			
			#once the file is written, we need to reset the reading pointer
			if self.file_read:
				self.reset()
			
			return True
			
		except:
			print "ERROR WHILE WRITING IN THE FILE %s" % (self.name,)
			return False
		
	
	#===
	#reading function, line by line or only one specific line
	def getLine(self):
		
		try:
			#this function ONLY opens the file, all other access should pass here
			if not self.file_read:
				self.file_read = open(self.name, 'r')
			
			line = self.file_read.readline()
			
			#we got a line? we increase the reading pointer
			if line:
				self.read_counter += 1
			
			return line
		
		except:
			print "ERROR WHILE READING THE FILE %s FOR LINE %i" % (self.name, num_)
			return False
	
	#===
	#simple function to read all the file
	#@return: list of lines
	def getAllLines(self):
	
		try:
			#le't be sure we are at the beginning
			if self.file_read:
				self.reset()
			
			#lets get the lines
			lines = []
			line = self.getLine()
			while line:
				lines.append(line.strip())
				#next line
				line = self.getLine()
			
			#lets count how many lines
			self.read_counter = len(lines)
			
			#lets return those lines
			return lines
		
		except:
			print "ERROR WHILE READING THE FILE %s " % (self.name, )
			return False
		
		
	#===
	#simple del function
	def delLine(self, line_num_):
		#new file content to be reconstructed
		new_file = ""
		
		try:
			#le't be sure we are at the beginning
			if self.file_read:
				self.reset()
			
			line = self.getLine()
			while line:
				if self.read_counter != line_num_:
					new_file += line
				else:
					print "line to be deleted : %s" %(line,)
				
				#next line
				line = self.getLine()
				
			#we close all pointers
			self.close()
			
			#we re-open the writing pointer
			self.file_write = open(self.name, 'w')	
			#next addLine() should append, if not, let's change here
			
			self.file_write.write(new_file)
			self.file_write.flush()
			
			return True
		
		except:
			print "ERROR WHILE DELETING A LINE IN THE FILE %s " % (self.name, )
			return False
