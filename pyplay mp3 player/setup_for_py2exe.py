from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
    windows = [{'script': "pyplay_mp3player_py34.py", 'icon_resources': [(0, 'headphone.ico'), (1, 'player_icon.ico'), (2, 'headphone_white.ico'),  (3, 'headphone_red.ico'),  (4, 'headphone_blue.ico')],}],
	options={'py2exe': {'bundle_files': 2}},
	zipfile = None, 
    version = '4.0',
    name = 'PyPlay MP3 Player',
    description = 'MP3 Music Player developed using Python 3.4',
    author = 'Dragos Vacariu',
    author_email='dragos.vacariu@mail.com',
)