"""
Simple py2exe setup file
Simonced@gmail.com
Compile line : python setup.py py2exe
"""

from distutils.core import setup
import py2exe
import glob

opts = {
	"py2exe": {
		"packages" : "encodings",
		"includes": ["atk", "gobject", "gtk", "cairo", "pango", "pangocairo"]
	}
}

setup(
	name = 'UrbanTerrorLauncher',
	description = 'A simple UrbanTerror Server bookmark manager',
	version = '0.8.1',
	windows = ['UrbanTerror_launcher.py'], 
	options = opts,
	data_files=[
		'UrbanTerror_launcher.txt',
		'UrbanTerror_buddies.txt',
		'UrbanTerror_launcher.cfg',
		'credits.txt',
		("rsc", glob.glob("rsc/*.png"))
	]
)