"""
Simple py2exe setup file
Simonced@gmail.com
Compile line : python setup.py py2exe
"""

from distutils.core import setup
import py2exe

setup(
	name = 'UrbanTerrorLauncher',
	description = 'A simple UrbanTerror Server bookmark manager',
	version = '0.7.4',
	console=['UrbanTerror_launcher.py'], 
	options = {
		'py2exe': {
			'packages':'encodings',
			'includes': 'cairo, pango, pangocairo, atk, gobject',
		}
	},
	data_files=[
		'UrbanTerror_launcher.txt',
		'UrbanTerror_launcher.cfg'
	]
)