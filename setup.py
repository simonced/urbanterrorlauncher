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
		"includes": ["pango", "atk", "gobject", "gtk", "cairo"]
	}
}

setup(
	name = 'UrbanTerrorLauncher',
	description = 'A simple UrbanTerror Server bookmark manager',
	version = '0.7.6',
	console=['UrbanTerror_launcher.py'], 
	options = opts,
	data_files=[
		'UrbanTerror_launcher.txt',
		'UrbanTerror_launcher.cfg',
		'credits.txt',
		("rsc", glob.glob("rsc/*.png"))
	]
)