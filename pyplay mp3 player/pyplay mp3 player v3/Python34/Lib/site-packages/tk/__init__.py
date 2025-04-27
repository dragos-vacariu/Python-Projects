# tk/__init__.py
# Rushy Panchal
# v1.0

'''tk includes extensions upon the native graphics in Python, Tkinter (or tkinter for Python 3.3.
It builds upon existing classes and widgets, adding increasing functionality.
'''

try:
	from Tkinter import *
except ImportError:
	from tkinter import *
import graphTools
import graphics
import tkBase
import tkExtra
import ttkExtra

modules = {
	'base': [
		'__init__.py',
		'graphics.py',
		'graphTools.py', 
		'tkExtra.py',
		'ttkExtra.py',
		'tkBase.py'
		],
	'latex': {
		'base': [
			'__init__.py',
			'Symbols.py'
			]
		}
	}

__author__ = "Rushy Panchal"

__version__ = 1.0
