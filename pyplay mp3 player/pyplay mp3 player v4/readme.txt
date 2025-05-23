This directory contains the Portable Version of Python310 and all the resources needed to run the script.

LEGEND:

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

The resources directory contains all the resources needed to run the script:
    clear.mp3 is a file used to clear the playback when making some changes for the file currently loaded.

The .PNG files from "installation of pip libraries guide" contains a guide upon how to install the libraries.

Presentation video: 
https://dragos-vacariu.github.io/catalogue/Python-Projects/PyPlay%20Mp3%20Player.html

Portable Downloads:
https://github.com/dragos-vacariu/Portable-Downloads/tree/main/PyPlay%20MP3%20Player

You can also use BUILD_EXECUTABLE_WITH_CXFREEZE.bat to build and executable from this script.

Web Page Presentation: 
https://dragos-vacariu.github.io/Html-Projects/Web%20Templates/project40%20python%20mp3%20player%20webpage/index.html