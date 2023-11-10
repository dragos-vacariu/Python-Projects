If the script crashes on startup, problem should be cause by the backup files.

Here is the legend of backup files for you to decide which to remove in these circumstances:

RENAMEALLFILES.backup -> is the file created to keep tracking of the initial names when using MASS FILE EDITOR.
In this file are stored the initial names of your .mp3 files. If you remove this, you will not be able
to undo Renaming performed by the Script to your files.

PREVIOUSALBUMYEAR.backup -> is the file created to keep tracking of the album/year changes when using MASS FILE EDITOR.
In this file is stored the initial tag value for album name/ year of the .mp3 files. If you remove this, you will not be able
to undo the changes performed by the Script to all your mp3 files.

PlayListBackup.pypl -> is the file which stores the details, and location of all the songs in 
your Playlist, if you remove this, the playlist is set to Defaults Skin & Colors and you might lose data like SongStats.


ALLARTISTTITLE.backup -> is the file created to keep tracking of the Artist and Title tags, when using
MASS FILE EDITOR to compose these 2 tags from FileName. If you remove this file, you will not be able to undo the changes
the Script has performed to all your Mp3 file Tags.

SongStats.sts -> is the file which will store information about each file in your library. Information such us: No. of Plays, Song Time 
Listened, Song Rating, Favorite Song, etc. The information is being taken from the Playlist which is currently loaded (which most of 
the time coincides with PlayListBackup.pypl), and gets transfered to SongStats.sts whenever the New Playlist button is hit. 

PlaylistReport.xlsx -> is the generated internal Report for the Playlist.

As long as you keep all your .backup files, you will always be able to undo any change the Script has done to your Mp3 Files.


The .PNG files from "installation of pip libraries guide" have no functional impact, they are just a guide of how 
to install libraries, in order to use this script.

clear.mp3 is a file used to clear the playback when making some changes for the file currently loaded.

Official Website:
https://pyplay-mp3player.site123.me


Presentation video: https://www.youtube.com/watch?v=uuD_buexn70&list=PLCma1j5Hgqtct-faQ8YIU9zQpXMgiIETA&index=2

Portable Downloads:

The cross-platform preinstalled version is also available on WEB at:
https://mega.nz/#F!GYxHjSgD!NM0715JCrPXXhfPERyLe-w

Windows Version:
https://github.com/dragos-vacariu/Portable-Downloads/blob/main/Python%20MP3%20Player%20compiled%20for%20windows.7z

setup_for_py2exe.py can be used to build and executable from this script.
The output of setup_for_py2exe and the resources need to be placed in the same directory.