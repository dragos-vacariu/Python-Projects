import datetime
import time
import pickle
import random
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter import StringVar
import os
import pygame
import re
from tkinter.ttk import Progressbar, Combobox
import sched, time
import sys
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from PIL import ImageTk, Image
import subprocess
import math
import shutil
import urllib3
from bs4 import BeautifulSoup
from abc import ABC
from tkinter import font
from urllib3.exceptions import NewConnectionError
from fractions import Fraction
from PIL import GifImagePlugin #used for animated gifs
from operator import itemgetter # used at saveSongStats
import codecs   #used at windowDialog constructor

import xlsxwriter #used to generate xls reports
import pynput #used for hotkeys
import psutil #used for application process / instances monitoring
from shared_memory_dict import SharedMemoryDict #used for shared memory across app instances
import webbrowser #used for opening web pages through the default web browser

#================================================================================
#tkinterdnd2 also known as tkdnd2 is used for enabling drag and drop over the window
from tkinterdnd2 import *  #COMMENT THIS LINES IF TKDND2 IS NOT SUPPORTED WITH PYINSTALLER OR PY2EXE

"""" workaround needed for pyinstaller to work with tkinterdnd2

When using software like Pyinstaller or auto-py-to-exe, certain pip installs, like tkinterDnD that are 
located in site-packages, do NOT get packed into your application - so you need to manually link to the 
tkinterDnD install directory location and pack the folder into the application manually:

content for .bat file to compile script with tkdnd2:
"""

"""
./Python310\Scripts/pyinstaller.exe" --add-data "./Python310/Lib/site-packages/tkinterdnd2/tkdnd:." ^
 --icon=./resources/headphone_red.ico -F ^
--noconsole pyplay_mp3player_py310.py
pause
"""

#class to encapsulate all needed variables for playlist.
class Playlist:
    def __init__(self):
        self.isSongPause = False
        self.isSongStopped = False
        self.VolumeLevel=1.0
        self.useMassFileEditor=False
        self.dirFilePath = []
        self.skin_theme = skinOptions[0]
        self.danthologyMode=False
        self.danthologyDuration=0
        self.danthologyTimer=0
        self.windowOpacity=1.0
        self.progressTime = "Ascending" #possible values: Ascending and Descending
        self.SHUFFLE = False
        self.isListOrdered = 21 #0-on songrating ; 1-sorted by name 2-sorted by name reversed; 3-random ....;
        self.validFiles = []
        self.slideImages = []
        self.slideImagesTransitionSeconds = 0;
        self.slideImagesTransitionSeconds = 0;
        self.usePlayerTitleTransition = False
        self.playingFileNameTransition = "separation" # values : separation, typewriting, none
        self.usingSlideShow = False
        self.slideImageIndex = 0
        self.currentSongIndex = None
        self.currentSongPosition = 0
        self.REPEAT = 1 # 1 is value for repeat all, 0 - repeat off, 2, repeat one, 3 - repeat none
        self.RESUMED=False
        self.viewModel = "PLAYLIST" # COMPACT value on this one will make the playList compact.
        self.playTime = 0
        self.userCreatedColors = []
        self.ProgressBarType = "determinate"
        self.LyricsActiveSource = LyricsOnlineSources[0] #default, all sources
        self.resetSettings = False
        self.useCrossFade = False
        self.crossFadeDuration = 10 #default value not customizable
        self.crossFadeGap = 3 #default value not customizable
        self.shufflingHistory = []
        self.playerXPos = 100 #Music player X coordinate
        self.playerYPos = 100 #Music player Y coordinate
        self.playerWidth = 300 #Music player Y coordinate
        self.playerHeight = 510 #Music player Y coordinate
        self.listboxNoRows = 20
        self.listboxWidth = 65
        self.buttonSpacing = 10 #default value
        self.keepSongsStats = True
        self.PlaylistListenedTime = 0
        self.useSongNameTitle = True
        self.BornDate = datetime.datetime.now()

#class to encapsulate all needed variables and function for a song
class Song:
    def __init__(self, filepath):
        self.filePath = formatSlashesInFilePath(filepath)
        self.fileName = getFileNameFromFilePath(self.filePath)

        self.fileSize = os.path.getsize(self.filePath) / (1024 * 1024)
        self.fileSize = float("{0:.2f}".format(self.fileSize))

        self.creation_time = os.path.getctime(self.filePath)
        self.modified_time = os.path.getmtime(self.filePath)
        self.Rating = 0
        self.NumberOfPlays = 0
        self.Exception = None
        try:
            audio = MP3(self.filePath)
            self.sample_rate = audio.info.sample_rate
            self.channels = audio.info.channels
            self.Length = audio.info.length
            self.SongListenedTime = 0
            self.bitrate = int(audio.info.bitrate / 1000)

            mp3 = MP3(self.filePath) # if the mp3 file has no tags, then the tags will be added to the file.
            if mp3.tags is None:
                mp3.add_tags()
                mp3.save()
            audio = EasyID3(self.filePath)
            try:
                self.Genre = audio["genre"]
            except: #enter here if you can't get the genre
                self.Genre = "Various"
            else:
                if len(self.Genre) > 0:
                    self.Genre = self.Genre[0]
                else:
                    self.Genre = "Various"
            try:
                self.Artist = audio["artist"]
            except:
                self.Artist = "Various"
            else:
                if len(self.Artist) > 0:
                    self.Artist = self.Artist[0]
                else:
                    self.Artist = "Various"
            try:
                self.Title = audio["title"]
            except:
                self.Title = "Various"
            else:
                if len(self.Title) > 0:
                    self.Title = self.Title[0]
                else:
                    self.Title = "Various"
            try:
                self.Year = audio["date"]
            except:
                self.Year = "Various"
            else:
                if len(self.Year) > 0:
                    self.Year = self.Year[0]
                else:
                    self.Year = "Various"
            try:
                self.Album = audio["album"]
            except:
                self.Album = "Various"
            else:
                if len(self.Album) > 0:
                    self.Album = self.Album[0]
                else:
                    self.Album = "Various"
            self.startPos = 0
            self.endPos = self.Length
            self.fadein_duration = 0
            self.fadeout_duration = 0
        except Exception as exp:
            self.Exception = exp

    def refreshSongData(self):
        if os.path.isfile(self.filePath):
            self.filePath = formatSlashesInFilePath(self.filePath)
            self.fileSize = os.path.getsize(self.filePath) / (1024 * 1024)
            self.fileSize = float("{0:.2f}".format(self.fileSize))

            self.creation_time = os.path.getctime(self.filePath)
            self.modified_time = os.path.getmtime(self.filePath)
            self.Exception = None
            try:
                audio = MP3(self.filePath)
                self.sample_rate = audio.info.sample_rate
                self.channels = audio.info.channels
                self.Length = audio.info.length
                self.bitrate = int(audio.info.bitrate / 1000)

                mp3 = MP3(self.filePath)  # if the mp3 file has no tags, then the tags will be added to the file.
                if mp3.tags is None:
                    mp3.add_tags()
                    mp3.save()
                audio = EasyID3(self.filePath)
                try:
                    self.Genre = audio["genre"]
                except:  # enter here if you can't get the genre
                    self.Genre = "Various"
                else:
                    if len(self.Genre) > 0:
                        self.Genre = self.Genre[0]
                    else:
                        self.Genre = "Various"
                try:
                    self.Artist = audio["artist"]
                except:
                    self.Artist = "Various"
                else:
                    if len(self.Artist) > 0:
                        self.Artist = self.Artist[0]
                    else:
                        self.Artist = "Various"
                try:
                    self.Title = audio["title"]
                except:
                    self.Title = "Various"
                else:
                    if len(self.Title) > 0:
                        self.Title = self.Title[0]
                    else:
                        self.Title = "Various"
                try:
                    self.Year = audio["date"]
                except:
                    self.Year = "Various"
                else:
                    if len(self.Year) > 0:
                        self.Year = self.Year[0]
                    else:
                        self.Year = "Various"
                try:
                    self.Album = audio["album"]
                except:
                    self.Album = "Various"
                else:
                    if len(self.Album) > 0:
                        self.Album = self.Album[0]
                    else:
                        self.Album = "Various"
                self.startPos = 0
                self.endPos = self.Length
                self.fadein_duration = 0
                self.fadeout_duration = 0
            except Exception as exp:
                self.Exception = exp
            index = play_list.validFiles.index(self)
            if index == play_list.currentSongIndex:
                #update the labels
                SongSize.set("Size: " + str(play_list.validFiles[play_list.currentSongIndex].fileSize) + " MB")
                if play_list.progressTime == "Ascending":
                    textProgress.set(
                        "Time Elapsed: " + formatTimeString(play_list.currentSongPosition))
                else:
                    textProgress.set("Time Left: " + formatTimeString(self.Length))
                # Update Length
                songLength = float("{0:.0f}".format(self.Length))  # no decimals needed
                textLength.set("Length: " + formatTimeString(songLength))
                textGenre.set("Genre: " + self.Genre)
                textArtist.set("Artist: " + self.Artist)
                textAlbum.set("Album: " + self.Album)
                textTitle.set("Title: " + self.Title)
                textYear.set("Year: " + self.Year)
                textStartTime.set("Starts at: " + formatTimeString(self.startPos))
                textEndTime.set("Ends at: " + formatTimeString(self.endPos))
                textFadeIn.set("FadeIn: " + str(self.fadein_duration) + "s")
                textFadeOut.set("FadeOut: " + str(self.fadeout_duration) + "s")
                mode = "Stereo" if play_list.validFiles[play_list.currentSongIndex].channels == 2 else "Mono"
                textMonoStereoMode.set("Mode: " + mode)
                textSampleRate.set("Sample Rate: " + str(self.sample_rate))
        else:
            #file is no longer available at the given filepath
            self.Exception = "File is no longer available."

    def __eq__(self, other):
        if self.filePath == other.filePath:
            return True
        else:
            return False

    def __repr__(self):
        if self in play_list.validFiles:
            return str(play_list.validFiles.index(self)) + ". " + str(self.fileName)
        else:
            return str(self.fileName) + "   " + str(formatTimeString(self.SongListenedTime)) +  "   " + str(self.NumberOfPlays)

#abstract class to encapsulate some common behavior for all our windowses
class Window(ABC): #let this class be abstract
    def destroyEsc(self,event):
        self.destroy()

    def destroy(self):
        self.top.destroy()
        self.top = None
        #if this is a WindowDialog object - they are stored in a list
        if self in windowCascade.WindowDialog:
            windowCascade.WindowDialog.remove(self)
        else:
            setattr(windowCascade, str(type(self).__name__), None)
        #windowCascade.reinitializeOpenedWindows()

    def take_focus(self):
        self.top.wm_attributes("-topmost", 1)

    def focus_out(self, event):
        windowCascade.root.wm_attributes("-topmost", 1)
        windowCascade.root.grab_set()
        windowCascade.root.focus_force()

    def thisWindowTitleUpdate(self, title: str):
        try:
            self.top.title(title)
            self.top.update()  # Force an update of the GUI
            #without this the window will freeze.
        except Exception as exp: pass

#a class to describe the behavior of a cutting / playback manager tool.
class CuttingTool(Window):
    def __init__(self, parent, fileIndex=None):
        global allButtonsFont
        color = PauseButton["bg"]  # get the color which the rest of elements is using at the moment
        self.index = play_list.currentSongIndex
        if fileIndex!=None:
            self.index = fileIndex
        if self.index != None:
            self.top = tk.Toplevel(parent, bg=color)
            self.top.protocol("WM_DELETE_WINDOW", self.destroy)
            self.Window_Title = "Cutting Tool"
            self.top.title(self.Window_Title)

            self.top_width = 410
            self.top_height = 350
            self.top.geometry(str(self.top_width) + "x" + str(self.top_height)+ "+"
                        + str(windowCascade.root.winfo_x()+100) + "+"
                        + str(windowCascade.root.winfo_y()+100))

            self.top.attributes('-alpha', play_list.windowOpacity)

            columnOne = 10
            columnTwo = 220
            vertical_space = 10

            labelInfoPosX = columnOne + 60

            self.InfoLabelText = StringVar()
            self.InfoLabelText.set("Welcome to MP3 Cutting capability:\n\n"
                               +"Please enter Start and End value and Hit OK.\n"
                                +"This will NOT change the original file.")
            self.infoLabel = tk.Label(self.top, textvariable=self.InfoLabelText, fg=fontColor.get(), font=allButtonsFont.get(), bg=color)
            self.infoLabel.place(x=labelInfoPosX, y=10)

            self.selectedFileLabel = tk.Label(self.top, text="Selected File: " + play_list.validFiles[self.index].fileName,
                                            fg=fontColor.get(), font=allButtonsFont.get(), bg=color)\

            positionTkWidgetsVertically(labelInfoPosX, self.infoLabel, self.selectedFileLabel, vertical_space)
            #self.selectedFileLabel.place(x=labelInfoPosX, y=100)

            self.selectedFileLabel["wraplength"] = self.infoLabel.winfo_reqwidth()


            self.startValueLabel = tk.Label(self.top, text="Start Value:",
                            fg=fontColor.get(), font=allButtonsFont.get(), bg=color)

            positionTkWidgetsVertically(columnOne, self.selectedFileLabel, self.startValueLabel, vertical_space)

            self.startValue = tk.Entry(self.top)
            positionTkWidgetsVertically(columnOne,self.startValueLabel, self.startValue, vertical_space)

            self.startValue.insert(tk.END, str(formatTimeString(play_list.validFiles[self.index].startPos)))
            self.startValue.bind("<Return>", self.cutItem)

            self.endValueLabel = tk.Label(self.top, text="End Value:", fg=fontColor.get(),
                          font=allButtonsFont.get(), bg=color)
            positionTkWidgetsVertically(columnOne, self.startValue, self.endValueLabel, vertical_space)

            self.endValue = tk.Entry(self.top)
            positionTkWidgetsVertically(columnOne, self.endValueLabel, self.endValue, vertical_space)
            self.endValue.insert(tk.END, str(formatTimeString(play_list.validFiles[self.index].endPos)))
            self.endValue.bind("<Return>", self.cutItem)

            self.buttonOK = tk.Button(self.top, text="Save Length", command=self.okButtonPressed, bg=color, fg=fontColor.get(), font=allButtonsFont.get())
            positionTkWidgetsVertically(columnOne, self.endValue, self.buttonOK, vertical_space)

            self.fadeInLabel = tk.Label(self.top, text="Add FadeIn: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color)
            positionTkWidgetsVertically(columnTwo, self.selectedFileLabel, self.fadeInLabel, vertical_space)

            self.FadeIn = StringVar()
            self.FadeIn.set(str(play_list.validFiles[self.index].fadein_duration))
            fadeOptions = ["5","10","15", "20"]
            self.fadeInBox = Combobox(self.top, textvariable=self.FadeIn, values=fadeOptions, state="readonly", font=allButtonsFont.get())
            self.fadeInBox.bind("<<ComboboxSelected>>", self.addFadeIn)

            positionTkWidgetsVertically(columnTwo, self.fadeInLabel, self.fadeInBox, vertical_space)

            self.fadeOutLabel = tk.Label(self.top, text="Add FadeOut: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color)
            positionTkWidgetsVertically(columnTwo, self.fadeInBox, self.fadeOutLabel, vertical_space)

            self.FadeOut = StringVar()
            self.FadeOut.set(str(play_list.validFiles[self.index].fadeout_duration))
            self.fadeOutBox = Combobox(self.top, textvariable=self.FadeOut, values=fadeOptions, state="readonly", font=allButtonsFont.get())

            positionTkWidgetsVertically(columnTwo, self.fadeOutLabel, self.fadeOutBox, vertical_space)

            self.fadeOutBox.bind("<<ComboboxSelected>>", self.addFadeOut)
            self.top.bind("<Escape>", self.destroyEsc)
            self.top.bind("<Tab>", self.focus_Input)
            self.addFadeInOutAll = tk.Button(self.top, text="Add Fading to All", command=self.addFadingOnPlaylist,
                                 bg=color, fg=fontColor.get(), font=allButtonsFont.get())

            positionTkWidgetsVertically(columnTwo, self.fadeOutBox, self.addFadeInOutAll, vertical_space)

            self.restoreButton = tk.Button(self.top, text="Restore Defaults for This Song", command=self.restoreCurrentSong, bg=color, fg=fontColor.get(), font=allButtonsFont.get())

            positionTkWidgetsVertically(80, self.addFadeInOutAll, self.restoreButton, vertical_space)

            self.restoreForAllButton = tk.Button(self.top, text="Restore Defaults for All Songs",
                                           command=self.restoreAllSongs, bg=color, fg=fontColor.get(),
                                           font=allButtonsFont.get())
            positionTkWidgetsVertically(80, self.restoreButton, self.restoreForAllButton, vertical_space)
            windowCascade.CuttingTool = self #each instance of CuttingTool will be assigned to this variable:


            elementsToCheckResize = list()
            elementsToCheckResize.append(self.infoLabel)
            elementsToCheckResize.append(self.selectedFileLabel)
            elementsToCheckResize.append(self.fadeOutBox)
            elementsToCheckResize.append(self.restoreForAllButton)

            calculateResizeWindow(self.top, elementsToCheckResize, 10)

    def addFadingOnPlaylist(self):
        global play_list
        message = ""
        i=0

        scheduler.suspend_mainloop()
        for song in play_list.validFiles:
            i+=1
            if scheduler.userIntervention == True:
                #user changed something in the play_list that might affect the outcome of this loop
                scheduler.userIntervention = False
                break
            self.top.title("Add Fading for: " + str(i) + " out of " + str(len(play_list.validFiles)) + " files")
            scheduler.single_loop() # this will make the main window responsive
            try:#without this try-except block the window will freeze.
                self.top.update()  # Force an update of the GUI
            except Exception as exp: pass
            if int(self.FadeIn.get()) + int(self.FadeOut.get()) > (song.endPos-song.startPos):
                message+= song.fileName + "\n"
            else:
                song.fadein_duration = int(self.FadeIn.get())
                song.fadeout_duration = int(self.FadeOut.get())

        scheduler.resume_mainloop()
        self.top.title(self.Window_Title)
        if message!= "":
            text = "Operation Done.\n\nFading was added to all Songs in the Playlist.\n\n" \
                    + "Some songs are too short for such long fading: " + message
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
        else:
            text = "Operation Done.\n\nFading was added to all Songs in the Playlist."
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None) , windowTitle = "Information")

    def restoreCurrentSong(self):
        global play_list
        play_list.validFiles[self.index].fadein_duration = 0
        play_list.validFiles[self.index].fadeout_duration = 0
        play_list.validFiles[self.index].startPos = 0
        play_list.validFiles[self.index].endPos = play_list.validFiles[self.index].Length
        self.FadeIn.set(str(play_list.validFiles[self.index].fadein_duration))
        self.FadeOut.set(str(play_list.validFiles[self.index].fadeout_duration))
        text = "Operation Done.\n\nCutting\Fading was removed from current Song."
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None) , windowTitle = "Information")
        textFadeIn.set("FadeIn: " + str(play_list.validFiles[self.index].fadein_duration)+"s")
        textFadeOut.set("FadeOut: " + str(play_list.validFiles[self.index].fadeout_duration)+"s")
        textEndTime.set("Ends at: " + formatTimeString(int(play_list.validFiles[self.index].endPos)))
        textStartTime.set("Starts at: " + formatTimeString(int(play_list.validFiles[self.index].startPos)))
        self.endValue.delete(0, tk.END)
        self.startValue.delete(0, tk.END)
        self.endValue.insert(tk.END, str(formatTimeString(play_list.validFiles[self.index].endPos)))
        self.startValue.insert(tk.END, str(formatTimeString(play_list.validFiles[self.index].startPos)))

    def restoreAllSongs(self):
        global play_list
        i=0

        scheduler.suspend_mainloop()
        for song in play_list.validFiles:
            i+=1
            if scheduler.userIntervention == True:
                #user changed something in the play_list that might affect the outcome of this loop
                scheduler.userIntervention = False
                break
            self.top.title("Undo Cutting\Fading for: " + str(i) + " out of " + str(len(play_list.validFiles)) + " files")
            scheduler.single_loop()# this will make the main window responsive
            try:#without this try-except block the window will freeze.
                self.top.update()  # Force an update of the GUI
            except Exception as exp: pass
            song.fadein_duration = 0
            song.fadeout_duration = 0
            song.startPos = 0
            song.endPos = song.Length

        scheduler.resume_mainloop()
        self.top.title(self.Window_Title)
        self.FadeIn.set(str(play_list.validFiles[self.index].fadein_duration))
        self.FadeOut.set(str(play_list.validFiles[self.index].fadeout_duration))
        text = "Operation Done.\n\nCutting\Fading was removed for all Songs in the Playlist."
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
        textFadeIn.set("FadeIn: " + str(play_list.validFiles[self.index].fadein_duration)+"s")
        textFadeOut.set("FadeOut: " + str(play_list.validFiles[self.index].fadeout_duration)+"s")
        textEndTime.set("Ends at: " + formatTimeString(int(play_list.validFiles[self.index].endPos)))
        textStartTime.set("Starts at: " + formatTimeString(int(play_list.validFiles[self.index].startPos)))
        self.endValue.delete(0, tk.END)
        self.startValue.delete(0, tk.END)
        self.endValue.insert(tk.END, str(formatTimeString(play_list.validFiles[self.index].endPos)))
        self.startValue.insert(tk.END, str(formatTimeString(int(play_list.validFiles[self.index].startPos))))

    def take_focus(self):
        self.top.wm_attributes("-topmost", 1)
        self.top.grab_set()
        self.startValue.focus_force()

    def focus_Input(self, event):
        if self.startValue.focus_get():
            self.endValue.focus_force()
        else:
            self.startValue.focus_force()

    def addFadeIn(self, event):
        global play_list
        if self.index !=None:
            if int(self.FadeIn.get()) + int(self.FadeOut.get()) > (play_list.validFiles[self.index].endPos-play_list.validFiles[self.index].startPos):
                text = "Song PlayTime is too short for these values."
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
            else:
                play_list.validFiles[self.index].fadein_duration = int(self.FadeIn.get())
            textFadeIn.set("FadeIn: " + str(play_list.validFiles[self.index].fadein_duration)+"s")
        showCurrentSongInList() #select/highlist the current song in the listbox

    def addFadeOut(self, event):
        global play_list
        if self.index!= None:
            if int(self.FadeIn.get()) + int(self.FadeOut.get()) > (play_list.validFiles[self.index].endPos-play_list.validFiles[self.index].startPos):
                text = "Song PlayTime is too short for these values."
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
            else:
                play_list.validFiles[self.index].fadeout_duration = int(self.FadeOut.get())
            textFadeOut.set("FadeOut: " + str(play_list.validFiles[self.index].fadeout_duration)+"s")
        showCurrentSongInList() #select/highlist the current song in the listbox

    def cutItem(self, event):
        self.okButtonPressed()

    def okButtonPressed(self):
        global dialog
        if self.startValue.get()!="" and self.index!=None:
            st_value = computeTimeToSeconds(self.startValue.get()) #let assume user entered a value in time format.
            if st_value < 0:
                try:
                    st_value = float(self.startValue.get())
                except:
                    text = "You have entered an invalid START value.\nCutting was aborted."
                    WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
                else:
                    if self.endValue.get() != "":
                        try:
                            ed_value = float(self.endValue.get())
                        except:
                            pass #don't say anything, the user will bey informed about this mistake in the next block
                        else:
                            if st_value > ed_value:
                                #interchange values
                                aux = st_value
                                st_value = ed_value
                                ed_value = aux
            if st_value >= 0 and st_value < play_list.validFiles[self.index].Length:
                play_list.validFiles[self.index].startPos = st_value
                startPos = int(play_list.validFiles[self.index].startPos)
                textStartTime.set("Starts at: " + formatTimeString(startPos))
            else:
                text = "Start Value is out of range.\nThe START was kept the same."
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
        if self.endValue.get() != "" and self.index!=None:
            ed_value = computeTimeToSeconds(self.endValue.get()) #let assume user entered a value in time format.
            if ed_value < 0:
                try:
                    ed_value = float(self.endValue.get())
                except:
                    text = "You have entered and invalid END value.\nCutting was aborted."
                    WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
                else:
                    if self.startValue.get() !="":
                        try:
                            st_value = float(self.startValue.get())
                        except:
                            pass #don't say anything, the user was already informed about this mistake.
                        else:
                            if st_value > ed_value:
                                #interchange values
                                aux = st_value
                                st_value = ed_value
                                ed_value = aux
            if ed_value > 0 and ed_value <= play_list.validFiles[self.index].Length:
                play_list.validFiles[self.index].endPos = ed_value
                endPos = int(play_list.validFiles[self.index].endPos)
                textEndTime.set("Ends at: " + formatTimeString(endPos))
            else:
                text = "End Value is out of range.\nThe END was kept the same."
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
        if (self.startValue.get()=="" and self.endValue.get() == ""):
            text = "You didn't entered any value, so the song was left untouched."
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

#a class to describe the behavior of a slideshow
class Slideshow(Window):
    def __init__(self):
        global allButtonsFont
        color = PauseButton["bg"]  # get the color which the rest of elements is using at the moment

        self.timer = 0
        self.seconds = None
        self.slide_image = None
        self.slideshow = None

        self.top = tk.Toplevel(windowCascade.root, bg=color)
        self.top.protocol("WM_DELETE_WINDOW", self.destroy)
        self.Window_Title = "Slideshow"
        self.top.title(self.Window_Title)
        self.top.geometry("300x300+" + str(windowCascade.root.winfo_x()+100) + "+" + str(windowCascade.root.winfo_y()+100))
        self.top.attributes('-alpha', play_list.windowOpacity)
        self.seconds = StringVar()
        if play_list.slideImagesTransitionSeconds != "0":
            self.seconds.set(play_list.slideImagesTransitionSeconds)
        else:
            self.seconds.set("1")
        durationOptions = [1,2,3,4,5,10,15,30,60]

        self.infoText = StringVar()
        self.infoText.set("Welcome to Slideshow!\n\n"+
                          "Please setup your slideshow before\n" +
                          "proceed or hit Continue Button\n"+
                          "(if available) to resume.\n\n" +
                          "Number of Seconds on Transition:")

        self.InfoLabel = tk.Label(self.top, textvariable=self.infoText, fg=fontColor.get(), font=allButtonsFont.get(),
                                  bg=color)
        self.InfoLabel.pack()

        self.imageDuration = Combobox(self.top, textvariable=self.seconds, values=durationOptions, state="readonly", font=allButtonsFont.get())
        self.imageDuration.pack(pady=5)
        self.imageDuration.bind("<<ComboboxSelected>>", self.time_set)
        self.loadImagesButton = tk.Button(self.top, text="Load Images",
                                                 command=self.loadImages, bg=color, fg=fontColor.get(),
                                                 font=allButtonsFont.get())
        self.loadImagesButton.pack(pady=10)
        self.clearImages = tk.Button(self.top, text="Clear Slideshow",
                                                 command=self.clearSlideshow, bg=color, fg=fontColor.get(),
                                                 font=allButtonsFont.get())
        self.clearImages.pack()
        self.startSlideshowButtonText = StringVar()
        if int(self.seconds.get()) > 0 and len(play_list.slideImages) > 0:
            self.startSlideshowButtonText.set("Continue")
        else:
            self.startSlideshowButtonText.set("Start")

        self.startSlideshow = tk.Button(self.top, textvariable = self.startSlideshowButtonText,
                                                 command=self.start, bg=color, fg=fontColor.get(),
                                                 font=allButtonsFont.get())
        self.startSlideshow.pack(pady=10)
        self.numberOfImages = StringVar()
        self.numberOfImages.set("Number of Images: " + str(len(play_list.slideImages)))
        self.labelNumberOfImages = tk.Label(self.top, textvariable=self.numberOfImages, fg=fontColor.get(), font=allButtonsFont.get(),
                                  bg=color)
        self.labelNumberOfImages.pack()
        self.top.bind("<Escape>", self.destroyEsc)
        self.top.bind("<Tab>", self.focus_out)
        windowCascade.Slideshow = self

    def loadImages(self):
        global play_list
        slidePictures = filedialog.askopenfilenames(initialdir="/", title="Please select one or more files", filetypes=(
        ("jpg files", "*.jpg"), ("png files", "*.png"),("gif files", "*.gif"), ("jpeg files", "*.jpeg")))
        play_list.slideImages += list(slidePictures)
        self.numberOfImages.set("Number of Images: " + str(len(play_list.slideImages)))

    def destroyEsc(self,event):
        self.destroy()

    def time_set(self,event):
        global play_list
        play_list.slideImagesTransitionSeconds = self.seconds.get()
        showCurrentSongInList() #select/highlight the current song in the listbox

    def clearSlideshow(self):
        play_list.slideImages.clear()
        self.seconds.set("1")
        self.startSlideshowButtonText.set("Start")
        self.numberOfImages.set("Number of Images: " + str(len(play_list.slideImages)))

    def destroy(self):
        Window.destroy(self) #calling parent destructor
        play_list.usingSlideShow = False
        self.timer = 0
        self.seconds = None
        self.slide_image = None
        self.slideshow = None
        self.top = None
        self.Window_Title = None

    def take_focus(self):
        self.top.wm_attributes("-topmost", 1)
        self.top.grab_set()
        self.top.focus_force()

    def countSeconds(self):
        if self.slide_image != None:
            #if the slideshow image is still valid or available at the location previously specified
            global play_list
            if (time.time() - self.timer) >= int(self.seconds.get()):
                if play_list.slideImageIndex+1 < len(play_list.slideImages):
                    play_list.slideImageIndex+=1
                else:
                    play_list.slideImageIndex = 0
                self.start()
            if self.slide_image.width() != self.top.winfo_width() or self.slide_image.height()!= self.top.winfo_height(): #this means window was resized()
                self.start() #this will redraw the image with the new size

    def start(self):
        global play_list
        if len(play_list.slideImages) > 0:
            try:
                self.timer = time.time()
                play_list.usingSlideShow = True
                self.slide_image = ImageTk.PhotoImage(Image.open(play_list.slideImages[play_list.slideImageIndex]).resize((self.top.winfo_width(), self.top.winfo_height()))) # open all kind of images like this
                self.slideshow = tk.Label(self.top, image=self.slide_image)
                self.slideshow.pack(fill="both")
                self.slideshow.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as exp:
                text = "Exception caught in Slideshow - Start function.\nMessage: " + str(exp)
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None) , windowTitle = "Warning")
        else:
            text = "Slideshow is empty. No valid files were found. \nPlease load only .jpg, .jpeg or .gif files."
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

#a class to describe the behavior of a sleeping/wakeup timer
class SleepingTool(Window):
    #static members
    timer = 0
    timeUntilEvent = 0
    eventType = None

    def __init__(self, parent):
        global allButtonsFont
        windowCascade.SleepingTool = self

        color = PauseButton["bg"]  # get the color which the rest of elements is using at the moment
        self.top = tk.Toplevel(parent, bg=color)
        self.top.protocol("WM_DELETE_WINDOW", self.destroy)
        Window_Title = "Sleeping Tool"
        self.top.title(Window_Title)
        self.top.geometry("300x230+" + str(windowCascade.root.winfo_x()+100) + "+" + str(windowCascade.root.winfo_y()+100))
        self.top.attributes('-alpha', play_list.windowOpacity)

        InfoLabelText = StringVar()
        InfoLabelText.set("Enter the time interval: \n")
        tk.Label(self.top , textvariable=InfoLabelText, fg=fontColor.get(), font=allButtonsFont.get(), bg=color).pack()
        tk.Label(self.top , text="Timer Value: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).pack()

        self.timeInterval = tk.Entry(self.top)
        self.timeInterval.insert(tk.END, str(formatTimeString(0)))

        self.timeInterval.pack(padx=5)
        SleepButton = tk.Button(self.top , text="Set Sleep Timer", command=self.setSleepingEvent, fg=fontColor.get(), font=allButtonsFont.get(), bg=color)
        SleepButton.pack(pady=10)

        wakeUpButton = tk.Button(self.top, text="Set WakeUp Timer", command=self.setWakeupEvent, fg=fontColor.get(), font=allButtonsFont.get(),
                                bg=color)
        wakeUpButton.pack(pady=5)

        disableTimersButton = tk.Button(self.top, text="Cancel Event", command=SleepingTool.cancelEvent, fg=fontColor.get(), font=allButtonsFont.get(),
                                bg=color)
        disableTimersButton.pack(pady=5)

        self.top.bind("<Escape>", self.destroyEsc)
        self.top.bind("<Tab>", self.focus_Input)

        #this will read/process the input just after the window is opened
        self.take_focus()
        self.focus_Input("<Key>")

    def eventSleeping(self, event):
        self.sleeping()

    def focus_Input(self, event):
        self.top.wm_attributes("-topmost", 1)
        self.timeInterval.focus_force()

    @staticmethod
    def cancelEvent():
        SleepingTool.timer = 0
        SleepingTool.eventType = None
        SleepingTool.timeUntilEvent = 0
        textWakeTimer.set("Wake Timer: NA")
        textSleepTimer.set("Sleep Timer: NA")

    def setSleepingEvent(self):
        SleepingTool.eventType = "sleeping"
        self.setEvent()

    def setWakeupEvent(self):
        SleepingTool.eventType = "wakeup"
        self.setEvent()

    def setEvent(self):
        if self.timeInterval.get() != "":
            SleepingTool.timeUntilEvent = computeTimeToSeconds(self.timeInterval.get()) #let assume user entered a value in time format.
            if SleepingTool.timeUntilEvent == 0:
                #if computeTimeToSeconds() cannot determine the number of seconds, then it will return -1
                #if SleepingTool.timeUntilEvent == 0 it means we have valid 0 entered by the user so reset the event
                SleepingTool.cancelEvent()
            if SleepingTool.timeUntilEvent > 0:
                if SleepingTool.eventType == "sleeping":
                    textWakeTimer.set("Wake Timer: NA")  # if it was supposed to wake up, overwrite that
                    textSleepTimer.set("Sleep Timer: " + formatTimeString(SleepingTool.timeUntilEvent))
                elif SleepingTool.eventType == "wakeup":
                    textWakeTimer.set("Wake Timer: " + formatTimeString(SleepingTool.timeUntilEvent))
                    textSleepTimer.set("Sleep Timer: NA")
                SleepingTool.timer = time.time()
            else: #maybe user entered only seconds
                try:
                    SleepingTool.timeUntilEvent = int(self.timeInterval.get())
                except Exception as exp:
                    text = "An invalid value was entered."
                    WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None) , windowTitle = "Information")
                else:
                    if SleepingTool.eventType == "sleeping":
                        textWakeTimer.set("Wake Timer: NA")
                        textSleepTimer.set("Sleep Timer: " + formatTimeString(SleepingTool.timeUntilEvent))
                    elif SleepingTool.eventType == "wakeup":
                        textWakeTimer.set("Wake Timer: " + formatTimeString(SleepingTool.timeUntilEvent))
                        textSleepTimer.set("Sleep Timer: NA")
                    SleepingTool.timer = time.time()

    @staticmethod
    def whenIsEvent():
        global play_list
        if SleepingTool.timer > 0 and APPLICATION_EXIT == False and SleepingTool.eventType != None:
            secondsLeft = int(SleepingTool.timeUntilEvent - (time.time() - SleepingTool.timer))
            if SleepingTool.eventType == "wakeup":
                textWakeTimer.set("Wake Timer: " + formatTimeString(secondsLeft))
            elif SleepingTool.eventType == "sleeping":
                textSleepTimer.set("Sleep Timer: " + formatTimeString(secondsLeft))
            if secondsLeft <= 0:
                SleepingTool.timeUntilEvent = 0
                if SleepingTool.eventType == "wakeup":
                    play_list.VolumeLevel = 1.0
                    VolumeScale.set(play_list.VolumeLevel * 100)
                    textWakeTimer.set("Wake Timer: NA")
                    SleepingTool.eventType = None
                    play_music()
                elif SleepingTool.eventType == "sleeping":
                    textSleepTimer.set("Sleep Timer: NA")
                    SleepingTool.eventType = None
                    stop_music()
        else: #timer was disabled
            textWakeTimer.set("Wake Timer: NA")
            textSleepTimer.set("Sleep Timer: NA")

#A class to describe the behavior of Customize window meant to be used to customize player settings
class Customize(Window):
    def __init__(self, parent):
        global allButtonsFont
        windowCascade.Customize = self
        global play_list
        color = PauseButton["bg"] # get the color which the rest of elements is using at the moment
        self.top = tk.Toplevel(parent, bg=color)
        self.top.protocol("WM_DELETE_WINDOW", self.destroy)
        Window_Title = "Customize"
        self.top.title(Window_Title)
        self.top.geometry("680x550+" + str(windowCascade.root.winfo_x()+100) + "+" + str(windowCascade.root.winfo_y()+100))
        self.top.attributes('-alpha', play_list.windowOpacity)
        columnOne = 10
        columnTwo = 250
        columnThree = 490

        startingYPos = 82
        verticalSpaceBetweenElements = 24
        yPositionForElement = startingYPos

        self.InfoLabelText = StringVar()
        self.InfoLabelText.set("Welcome to Customize capability:\n\n"
                                +"Here you can customize your player appearance\n"
                                 +"in any way you like.\n")
        tk.Label(self.top, textvariable=self.InfoLabelText, fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=180, y=5)

        self.labelFontColor = tk.Label(self.top, text="Button / Label Color: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color)
        self.labelFontColor.place(x=columnOne, y=yPositionForElement)

        yPositionForElement+=verticalSpaceBetweenElements

        self.colorBox = Combobox(self.top, textvariable=SkinColor, values=custom_color_list, state="readonly", font=allButtonsFont.get())
        self.colorBox.place(x=columnOne, y=yPositionForElement)
        self.colorBox.bind("<<ComboboxSelected>>", self.changingBackgroundElementColor)

        yPositionForElement += verticalSpaceBetweenElements

        tk.Label(self.top, text="Font: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=columnOne, y=yPositionForElement)

        #elements could be placed vertically using positionTkWidgetsVertically instead of recalculating yPositionForElement
        yPositionForElement += verticalSpaceBetweenElements

        self.fontBox = Combobox(self.top, textvariable=allButtonsFont, values=custom_font_list, state="readonly", font=allButtonsFont.get())
        self.fontBox.place(x=columnOne, y=yPositionForElement)
        self.fontBox.bind("<<ComboboxSelected>>", self.customFontChange)

        yPositionForElement += verticalSpaceBetweenElements

        tk.Label(self.top, text="Label Background: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=10, y=yPositionForElement)
        self.labelColorBox = Combobox(self.top, textvariable=labelBackground, values=custom_color_list, state="readonly", font=allButtonsFont.get())

        yPositionForElement += verticalSpaceBetweenElements

        self.labelColorBox.place(x=columnOne, y=yPositionForElement)
        self.labelColorBox.bind("<<ComboboxSelected>>", self.changingLabelBackgroundColor)

        yPositionForElement += verticalSpaceBetweenElements

        tk.Label(self.top, text="Font Color: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=columnOne, y=yPositionForElement)
        self.FontMainColorBox = Combobox(self.top, textvariable=fontColor, values=custom_color_list, state="readonly", font=allButtonsFont.get())

        yPositionForElement += verticalSpaceBetweenElements

        self.FontMainColorBox.place(x=columnOne, y=yPositionForElement)
        self.FontMainColorBox.bind("<<ComboboxSelected>>", self.changingFontColor)

        yPositionForElement += verticalSpaceBetweenElements

        tk.Label(self.top, text="Playing Label Transition: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=columnOne, y=yPositionForElement)
        self.FontTransitionText = StringVar()

        yPositionForElement += verticalSpaceBetweenElements

        self.FontTransitionText.set(play_list.playingFileNameTransition)
        self.FontTransitionBox = Combobox(self.top, textvariable=self.FontTransitionText, values=["none", "separation", "typewriting"], \
                                            state="readonly", font=allButtonsFont.get())
        self.FontTransitionBox.place(x=columnOne, y=yPositionForElement)
        self.FontTransitionBox.bind("<<ComboboxSelected>>", self.changeFileNameTransition)


        yPositionForElement += verticalSpaceBetweenElements

        tk.Label(self.top, text="Color Picker Result Usage: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=columnOne, y=yPositionForElement)
        self.textColorPickerUsage = StringVar()
        self.textColorPickerUsage.set("No Usage")

        yPositionForElement += verticalSpaceBetweenElements

        self.ColorPickerUsage = Combobox(self.top, textvariable=self.textColorPickerUsage, font=allButtonsFont.get(),
                                         values=["No Usage", "Button / Label Color", "Label Background", "Font Color"], state="readonly")
        self.ColorPickerUsage.place(x=columnOne, y=yPositionForElement)
        self.ColorPickerUsage.bind("<<ComboboxSelected>>", self.useColorPicked)

        yPositionForElement += verticalSpaceBetweenElements

        tk.Label(self.top, text="ProgressBar Type: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=columnOne, y=yPositionForElement)
        self.textProgressBarType = StringVar()
        self.textProgressBarType.set(play_list.ProgressBarType)

        yPositionForElement += verticalSpaceBetweenElements

        self.ProgressBarTypeBox = Combobox(self.top, textvariable=self.textProgressBarType, state="readonly",
                                         values=["determinate", "indeterminate"], font=allButtonsFont.get())
        self.ProgressBarTypeBox.place(x=columnOne, y=yPositionForElement)
        self.ProgressBarTypeBox.bind("<<ComboboxSelected>>", self.changeProgressBar)

        yPositionForElement += verticalSpaceBetweenElements

        tk.Label(self.top, text="Playlist Max. Rows: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(
            x=columnOne, y=yPositionForElement)
        self.textPlaylistRows = StringVar()
        self.textPlaylistRows.set(str(play_list.listboxNoRows))

        yPositionForElement += verticalSpaceBetweenElements

        self.PlaylistNoRowsBox = Combobox(self.top, textvariable=self.textPlaylistRows, state="readonly", font=allButtonsFont.get(),
                                           values=["20","21","22","23","24","25", "26", "27", "28", "29", "30"])
        self.PlaylistNoRowsBox.place(x=columnOne, y=yPositionForElement)
        self.PlaylistNoRowsBox.bind("<<ComboboxSelected>>", self.changePlaylistHeight)

        yPositionForElement += verticalSpaceBetweenElements

        self.crossFadeBetweenTracks = tk.IntVar()
        self.crossFadeBetweenTracks.set(int(play_list.useCrossFade))
        tk.Checkbutton(self.top, text="Use cross-fading.", fg=fontColor.get(), font=allButtonsFont.get(),
                       bg=color, variable=self.crossFadeBetweenTracks, command=self.enableDisableCrossFade,
                       selectcolor="black").place(x=columnOne, y=yPositionForElement)

        yPositionForElement = startingYPos

        self.TitleTransitionButtonText = StringVar()
        if play_list.usePlayerTitleTransition == True:
            self.TitleTransitionButtonText.set("Title Transition ON")
        else:
            self.TitleTransitionButtonText.set("Title Transition OFF")

        self.TitleTransition = tk.Button(self.top, textvariable=self.TitleTransitionButtonText, command=self.changeTitleTransition, bg=color, fg=fontColor.get(),
                                        font=allButtonsFont.get())
        self.TitleTransition.place(x=columnTwo, y=yPositionForElement)

        yPositionForElement += verticalSpaceBetweenElements+10 #+10 because next element is button

        tk.Label(self.top, text="Unique Text Color?", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=columnTwo, y=yPositionForElement)
        self.colorBgLabels = tk.IntVar()
        if labelPlaying["fg"] == PauseButton["fg"]:
            self.colorBgLabels.set(1)
        else:
            self.colorBgLabels.set(0)

        rbFgColor = fontColor.get() if fontColor.get() != "black" else "white"

        self.RbFalse = tk.Radiobutton(self.top, text="False", variable=self.colorBgLabels, value=0, width=5, bg=color,
                            command=self.changingBackgroundedLabelsColor, fg=rbFgColor, selectcolor="black", font=allButtonsFont.get())
        self.RbTrue = tk.Radiobutton(self.top, text="True", variable=self.colorBgLabels, value=1, width=5, bg=color,
                            command=self.changingBackgroundedLabelsColor, fg=rbFgColor, selectcolor="black", font=allButtonsFont.get())

        yPositionForElement += verticalSpaceBetweenElements
        self.RbFalse.place(x=columnTwo, y=yPositionForElement)
        self.RbTrue.place(x=columnTwo+80, y=yPositionForElement)

        yPositionForElement += verticalSpaceBetweenElements

        self.browseBackgroundPicture = tk.Button(self.top, text="Load Background", command=self.browse_background_picture, bg=color, fg=fontColor.get(),
                                                 font=allButtonsFont.get())
        self.browseBackgroundPicture.place(x=columnTwo, y=yPositionForElement)

        yPositionForElement += verticalSpaceBetweenElements+10 #+10 because next element is button

        self.startSlideshow = tk.Button(self.top, text="Start Slideshow", command=showSlideshowWindow, bg=color, fg=fontColor.get(), font=allButtonsFont.get())
        self.startSlideshow.place(x=columnTwo, y=yPositionForElement)

        yPositionForElement += verticalSpaceBetweenElements + 10  # +10 because previous element was button

        tk.Label(self.top, text="Window Opacity: ", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnTwo, y=yPositionForElement)
        self.WindowOpacityText = StringVar()
        self.WindowOpacityText.set(play_list.windowOpacity)

        yPositionForElement += verticalSpaceBetweenElements

        self.WindowOpacityBox = Combobox(self.top, textvariable=self.WindowOpacityText, state="readonly", font=allButtonsFont.get(),
                                          values=["1.0", "0.9", "0.8", "0.7", "0.6", "0.5"])
        self.WindowOpacityBox.place(x=columnTwo, y=yPositionForElement)
        self.WindowOpacityBox.bind("<<ComboboxSelected>>", self.changeWindowOpacity)

        yPositionForElement += verticalSpaceBetweenElements

        tk.Label(self.top, text="Progress Time: ", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnTwo, y=yPositionForElement)

        self.ProgressTimeText = StringVar()
        if play_list.progressTime == "Ascending":
            self.ProgressTimeText.set("Playing Time")
        else:
            self.ProgressTimeText.set("Remaining Time")

        yPositionForElement += verticalSpaceBetweenElements
        self.ProgressTimeBox = Combobox(self.top, textvariable=self.ProgressTimeText, state="readonly", font=allButtonsFont.get(),
                                         values=["Playing Time", "Remaining Time"])
        self.ProgressTimeBox.place(x=columnTwo, y=yPositionForElement)
        self.ProgressTimeBox.bind("<<ComboboxSelected>>", self.changeProgressTime)

        yPositionForElement += verticalSpaceBetweenElements

        tk.Label(self.top, text="Lyrics Active Source: ", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnTwo, y=yPositionForElement)
        self.LyricsSourcesText = StringVar()
        self.LyricsSourcesText.set(play_list.LyricsActiveSource)

        yPositionForElement += verticalSpaceBetweenElements

        self.LyricsSourcesBox = Combobox(self.top, textvariable=self.LyricsSourcesText,  state="readonly", font=allButtonsFont.get(),
                                         values=LyricsOnlineSources)
        self.LyricsSourcesBox.place(x=columnTwo, y=yPositionForElement)
        self.LyricsSourcesBox.bind("<<ComboboxSelected>>", self.changeActiveLyricsSource)

        yPositionForElement += verticalSpaceBetweenElements

        tk.Label(self.top, text="Playlist Width: ", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnTwo, y=yPositionForElement)
        self.textPlaylistWidth = StringVar()
        self.textPlaylistWidth.set(play_list.listboxWidth)

        yPositionForElement += verticalSpaceBetweenElements

        self.PlaylistWidthBox = Combobox(self.top, textvariable=self.textPlaylistWidth, state="readonly", font=allButtonsFont.get(),
                                 values=["65", "70", "75", "80", "85", "90", "95", "100", "105", "110"])
        self.PlaylistWidthBox.place(x=columnTwo, y=yPositionForElement)
        self.PlaylistWidthBox.bind("<<ComboboxSelected>>", self.changePlaylistWidth)

        yPositionForElement += verticalSpaceBetweenElements+10 #+10 because next element is a button

        RestoreDefaultsButton = tk.Button(self.top, text="Restore Defaults", command=self.restoreDefaults, fg=fontColor.get(), font=allButtonsFont.get(),
                                bg=color)
        RestoreDefaultsButton.place(x=columnTwo, y=yPositionForElement)

        self.textDanthologyMode = StringVar()

        if play_list.danthologyMode == True:
            self.textDanthologyMode.set("Danthology Mode ON")
        else:
            self.textDanthologyMode.set("Danthology Mode OFF")

        yPositionForElement = startingYPos
        self.danthologyMode = tk.Button(self.top, textvariable=self.textDanthologyMode, command=self.changeDanthologyMode, bg=color, fg=fontColor.get(),
                                        font=allButtonsFont.get())
        self.danthologyMode.place(x=columnThree, y=yPositionForElement)
        text = "Danthology refers to resuming the next song at the duration the current one " \
               "has ended. This feature enables easier browse among unknown media."
        ToolTip(self.danthologyMode, text)
        self.DanthologyInterval = StringVar()
        self.DanthologyInterval.set(play_list.danthologyDuration)

        yPositionForElement += verticalSpaceBetweenElements+10 #+10 because previous element was button

        tk.Label(self.top, text="Danthology Duration: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=columnThree, y=yPositionForElement)
        self.DanthologySetBox = Combobox(self.top, textvariable=self.DanthologyInterval, values=["0", "10", "30", "60", "90"], state="readonly", font=allButtonsFont.get())

        yPositionForElement += verticalSpaceBetweenElements

        self.DanthologySetBox.place(x=columnThree, y=yPositionForElement)
        self.DanthologySetBox.bind("<<ComboboxSelected>>", self.changeDanthologyDuration)

        yPositionForElement += verticalSpaceBetweenElements

        tk.Label(self.top, text="Color Picker: ", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnThree, y=yPositionForElement)

        yPositionForElement += verticalSpaceBetweenElements

        self.scaleRed = tk.Scale(self.top, from_=0, to=255, orient=tk.HORIZONTAL, fg=fontColor.get(), font=allButtonsFont.get(), bg=color, length=140, \
                                 sliderlength=10, width=10, bd=1, label="Red:")

        self.scaleRed.place(x=columnThree, y=yPositionForElement)
        self.scaleRed.bind("<ButtonRelease-1>", self.composeColor)

        self.scaleGreen = tk.Scale(self.top, from_=0, to=255, orient=tk.HORIZONTAL, fg=fontColor.get(), length=140, \
                            font=allButtonsFont.get(), bg=color, sliderlength=10, width=10, bd=1, label="Green:")

        yPositionForElement += verticalSpaceBetweenElements+40 #+40 because previous element was a scale
        self.scaleGreen.place(x=columnThree, y=yPositionForElement)
        self.scaleGreen.bind("<ButtonRelease-1>", self.composeColor)

        self.scaleBlue = tk.Scale(self.top, from_=0, to=255, orient=tk.HORIZONTAL, fg=fontColor.get(),  length=140, \
                            font=allButtonsFont.get(), bg=color, sliderlength=10, width=10, bd=1, label="Blue:")

        yPositionForElement += verticalSpaceBetweenElements + 40  # +40 because previous element was a scale
        self.scaleBlue.place(x=columnThree, y=yPositionForElement)
        self.scaleBlue.bind("<ButtonRelease-1>", self.composeColor)

        yPositionForElement += verticalSpaceBetweenElements + 40  # +40 because previous element was a scale
        self.ColorPickerResult = tk.Label(self.top, text="  Color Picker Result  ", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg="black")
        self.ColorPickerResult.place(x=columnThree, y=yPositionForElement)

        yPositionForElement += verticalSpaceBetweenElements

        self.textButtonSpace = StringVar()
        self.textButtonSpace.set(str(play_list.buttonSpacing))
        tk.Label(self.top, text="Element Spacing: ", fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(
            x=columnThree, y=yPositionForElement)
        self.buttonSpacingBox = Combobox(self.top, textvariable=self.textButtonSpace,
                                         values=["10", "15", "20", "25", "30", "35", "40", "45", "50", "55", "60"], state="readonly",
                                         font=allButtonsFont.get())

        yPositionForElement += verticalSpaceBetweenElements
        self.buttonSpacingBox.place(x=columnThree, y=yPositionForElement)
        self.buttonSpacingBox.bind("<<ComboboxSelected>>", self.changeButtonSpacing)

        self.songNameTitle = tk.IntVar()
        self.songNameTitle.set(int(play_list.useSongNameTitle))

        yPositionForElement += verticalSpaceBetweenElements
        self.useSongNameCheckbox = tk.Checkbutton(self.top, text="Use Song name as Title.", fg=fontColor.get(), font=allButtonsFont.get(),
                       bg=color, variable=self.songNameTitle, command=self.useProjectSongTitle,
                       selectcolor="black")

        self.useSongNameCheckbox.place(x=columnThree, y=yPositionForElement)

        self.MaintainSongsStats = tk.IntVar()
        self.MaintainSongsStats.set(int(play_list.keepSongsStats))

        yPositionForElement = 470

        tk.Checkbutton(self.top, text="Maintain Songs Stats on All Playlists.", fg=fontColor.get(), font=allButtonsFont.get(),
                       bg=color, variable=self.MaintainSongsStats, command=self.enableDisableSongsStatsKeeping,
                       selectcolor="black").place(x=200, y=yPositionForElement)

        self.MassFileEditorUsage = tk.IntVar()
        self.MassFileEditorUsage.set(play_list.useMassFileEditor)

        yPositionForElement += verticalSpaceBetweenElements

        tk.Checkbutton(self.top, text="Use mass file editor capabilities.", fg=fontColor.get(), font=allButtonsFont.get(),
                       bg=color, variable=self.MassFileEditorUsage, command=self.enableDisableMassFileEditor,
                       selectcolor="black").place(x=200, y=yPositionForElement)

        yPositionForElement += verticalSpaceBetweenElements

        self.resetSettingsVar = tk.IntVar()
        self.resetSettingsVar.set(int(play_list.resetSettings))
        self.resetSettingsCheckbox = tk.Checkbutton(self.top, text="Reset Settings on New Playlist.", fg=fontColor.get(), font=allButtonsFont.get(),
                       bg=color, variable=self.resetSettingsVar, command=self.resetSettingsOnNewPlaylist,
                       selectcolor="black")
        self.resetSettingsCheckbox.place(x=200, y=yPositionForElement)
        self.top.bind("<Escape>", self.destroyEsc)
        self.top.bind("<Tab>", self.focus_Input)

        calculateResizeWindow(self.top, [self.DanthologySetBox, self.scaleGreen,
                 self.ColorPickerResult, self.useSongNameCheckbox, self.resetSettingsCheckbox], 10)

    def customFontChange(self, event):
        global play_list
        play_list.skin_theme.font = allButtonsFont.get()
        customFontChange(event)
        updateSkinMenuLabels()
        windowCascade.reinitializeOpenedWindows()

    def changingFontColor(self, event):
        global play_list
        play_list.skin_theme.button_font_color = fontColor.get()
        changingFontColor(event)
        updateRadioButtons()
        updateSkinMenuLabels()
        windowCascade.reinitializeOpenedWindows()

    def changingLabelBackgroundColor(self, event): #creating owned function for changing element style with windowCascade reinitialized
        # if user picked up the color for the used predefined skin
        global play_list
        play_list.skin_theme.label_bg_color = labelBackground.get()
        changingLabelBackgroundColor(event)
        updateRadioButtons()
        updateSkinMenuLabels()
        windowCascade.reinitializeOpenedWindows()

    def changingBackgroundElementColor(self, event): #creating owned function for changing element style with windowCascade reinitialized
        #if user picked up the color for the used predefined skin
        global play_list
        play_list.skin_theme.background_color = SkinColor.get()
        changingBackgroundElementColor(event)
        updateSkinMenuLabels()
        updateRadioButtons()
        showCurrentSongInList()
        windowCascade.reinitializeOpenedWindows()

    def changingBackgroundedLabelsColor(self):
        global play_list
        if labelPlaying["fg"] != PauseButton["fg"]:
            play_list.skin_theme.unique_font_color = True
        else:
            play_list.skin_theme.unique_font_color = False
        changingBackgroundedLabelsColor()
        updateSkinMenuLabels()
        updateRadioButtons()
        showCurrentSongInList()
        windowCascade.reinitializeOpenedWindows()

    def enableDisableSongsStatsKeeping(self):
        global play_list
        if self.MaintainSongsStats.get() == 1:
            play_list.keepSongsStats = True
        else:
            play_list.keepSongsStats = False

    def changeButtonSpacing(self, event):
        play_list.buttonSpacing = int(self.textButtonSpace.get())
        reSpacePositionElements()  # respace elements
        showCurrentSongInList() #select/highlight the current song in the listbox

    def changePlaylistWidth(self, event):
        play_list.listboxWidth = int(self.textPlaylistWidth.get())
        listbox["width"] = play_list.listboxWidth
        readjustSearchFormWidth()
        changePlaylistView()  # this will rearrange elements and resize the window.
        showCurrentSongInList()  # select/highlight the current song in the listbox

    def changePlaylistHeight(self, event):
        play_list.listboxNoRows = int(self.textPlaylistRows.get())
        if play_list.viewModel!= "COMPACT":
            changePlaylistView()
        showCurrentSongInList() #select/highlight the current song in the listbox

    def restoreDefaults(self):
        global play_list
        global windowCascade
        play_list.useMassFileEditor=False
        play_list.danthologyMode=False
        play_list.danthologyDuration=0
        play_list.danthologyTimer=0
        play_list.windowOpacity=1.0
        play_list.progressTime = "Ascending" #possible values: Ascending and Descending
        play_list.usePlayerTitleTransition = False
        if play_list.currentSongIndex != None:
            Project_Title = "   " + play_list.validFiles[play_list.currentSongIndex].fileName + "   "
        else:
            Project_Title = "   PyPlay MP3 Player in Python     "
        windowCascade.root.title(Project_Title)
        play_list.playingFileNameTransition = "separation" # values : separation, typewriting, none
        play_list.skin_theme = skinOptions[0]
        play_list.userCreatedColors = []
        play_list.ProgressBarType = "determinate"
        play_list.LyricsActiveSource = LyricsOnlineSources[0] #default, all sources
        play_list.resetSettings = False
        play_list.useCrossFade = False
        play_list.useSongNameTitle = True
        windowCascade.root.attributes('-alpha', play_list.windowOpacity)
        # Restore default skin
        play_list.listboxWidth = 65
        play_list.listboxNoRows = 20
        play_list.buttonSpacing = 10
        play_list.keepSongsStats = True
        play_list.skin_theme.changingSkin()
        #displayElementsOnPlaylist()

    def resetSettingsOnNewPlaylist(self):
        if self.resetSettingsVar.get() == 1:
            play_list.resetSettings = True
        else:
            play_list.resetSettings = False

    def changeActiveLyricsSource(self, event):
        play_list.LyricsActiveSource = self.LyricsSourcesText.get()
        showCurrentSongInList() #select/highlight the current song in the listbox

    def changeProgressBar(self, event):
        global play_list
        global progress
        play_list.ProgressBarType = self.textProgressBarType.get()
        progress["mode"] = play_list.ProgressBarType
        showCurrentSongInList() #select/highlight the current song in the listbox

    def enableDisableMassFileEditor(self):
        global play_list
        if self.MassFileEditorUsage.get() == 1:
            play_list.useMassFileEditor = True
        else:
            play_list.useMassFileEditor = False

    def enableDisableCrossFade(self):
        global play_list
        global temp_SongEndPos
        if len(play_list.validFiles) > 0 and play_list.currentSongIndex!=None:
            if self.crossFadeBetweenTracks.get() == 1:
                play_list.validFiles[play_list.currentSongIndex].fadein_duration = play_list.crossFadeDuration
                play_list.validFiles[play_list.currentSongIndex].fadeout_duration = play_list.crossFadeDuration
                temp_SongEndPos = play_list.validFiles[play_list.currentSongIndex].endPos
                play_list.validFiles[play_list.currentSongIndex].endPos = (play_list.validFiles[play_list.currentSongIndex].Length - play_list.crossFadeGap*3)
                play_list.useCrossFade = True
            else:
                play_list.validFiles[play_list.currentSongIndex].fadein_duration = 0
                play_list.validFiles[play_list.currentSongIndex].fadeout_duration = 0
                if temp_SongEndPos!= None:
                    play_list.validFiles[play_list.currentSongIndex].endPos = temp_SongEndPos
                else: #this should never happen.
                    play_list.validFiles[play_list.currentSongIndex].endPos = play_list.validFiles[play_list.currentSongIndex].Length
                play_list.useCrossFade = False

    def useProjectSongTitle(self):
        global play_list
        global Project_Title
        if play_list.useSongNameTitle:
            play_list.useSongNameTitle = False
            Project_Title = "   PyPlay MP3 Player in Python     "
            windowCascade.root.title(Project_Title)
        else:
            play_list.useSongNameTitle = True
            if play_list.currentSongIndex != None:
                Project_Title = "   " + play_list.validFiles[play_list.currentSongIndex].fileName + "   "
            else:
                Project_Title = "   PyPlay MP3 Player in Python     "
            windowCascade.root.title(Project_Title)
        self.songNameTitle.set(int(play_list.useSongNameTitle))

    def changeProgressTime(self, event):
        global play_list
        if self.ProgressTimeText.get() == "Playing Time":
            play_list.progressTime = "Ascending"
            textProgress.set(textProgress.get().replace("Time Left: ", "Time Elapsed: "))
        else:
            play_list.progressTime = "Descending"
            textProgress.set(textProgress.get().replace("Time Elapsed: ", "Time Left: "))
        showCurrentSongInList() #select/highlight the current song in the listbox

    def useColorPicked(self, event):
        global SkinColor
        global labelBackground
        global fontColor
        if hasattr(self, "ColorPickerValue"):
            updateSkinMenuLabels()
            if self.ColorPickerValue!="":
                if self.textColorPickerUsage.get() == "Button / Label Color":
                    SkinColor.set(self.ColorPickerValue)
                    play_list.userCreatedColors.append(self.ColorPickerValue)
                    custom_color_list.append(self.ColorPickerValue)
                    changingBackgroundElementColor(event)
                    updateRadioButtons()
                    showCurrentSongInList()
                elif self.textColorPickerUsage.get() == "Label Background":
                    labelBackground.set(self.ColorPickerValue)
                    play_list.userCreatedColors.append(self.ColorPickerValue)
                    custom_color_list.append(self.ColorPickerValue)
                    changingLabelBackgroundColor(event)
                    updateRadioButtons()
                elif self.textColorPickerUsage.get() == "Font Color":
                    fontColor.set(self.ColorPickerValue)
                    play_list.userCreatedColors.append(self.ColorPickerValue)
                    custom_color_list.append(self.ColorPickerValue)
                    changingFontColor(event)
                    updateRadioButtons()
            showCurrentSongInList() #select/highlight the current song in the listbox
        else:
            text = "Please Use the Color Picker to create a color."
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
        windowCascade.reinitializeOpenedWindows()

    def composeColor(self, event):
        global custom_color_list
        red = ""
        if int(self.scaleRed.get()) >=0 and  int(self.scaleRed.get()<10):
            red = str(hex(self.scaleRed.get()))
            red=red.split("x")
            red= "0" + red[1]
        else:
            red = str(hex(self.scaleRed.get()))
            red = red.split("x")
            red = red[1]

        green = ""
        if int(self.scaleGreen.get()) >= 0 and int(self.scaleGreen.get() < 10):
            green = str(hex(self.scaleGreen.get()))
            green = green.split("x")
            green = "0" + green[1]
        else:
            green = str(hex(self.scaleGreen.get()))
            green = green.split("x")
            green = green[1]

        blue = ""
        if int(self.scaleBlue.get()) >= 0 and int(self.scaleBlue.get() < 10):
            blue = str(hex(self.scaleBlue.get()))
            blue = blue.split("x")
            blue = "0" + blue[1]
        else:
            blue = str(hex(self.scaleBlue.get()))
            blue = blue.split("x")
            blue = blue[1]

        self.ColorPickerValue = "#" + red + green + blue
        self.ColorPickerResult["bg"] = self.ColorPickerValue

    def changeDanthologyDuration(self, event):
        global play_list
        play_list.danthologyDuration = int(self.DanthologyInterval.get())
        play_list.danthologyTimer = time.time()
        showCurrentSongInList() #select/highlight the current song in the listbox

    def changeWindowOpacity(self,event):
        global play_list
        play_list.windowOpacity = float(self.WindowOpacityText.get())
        windowCascade.root.attributes('-alpha', play_list.windowOpacity)
        self.top.attributes('-alpha', play_list.windowOpacity)
        showCurrentSongInList() #select/highlight the current song in the listbox
        windowCascade.reinitializeOpenedWindows()

    def changeDanthologyMode(self):
        global play_list
        if play_list.danthologyMode == True:
            play_list.danthologyMode = False
            self.textDanthologyMode.set("Danthology Mode OFF")
            textDanthologyMode.set("Danthology: OFF")
        else:
            play_list.danthologyMode = True
            self.textDanthologyMode.set("Danthology Mode ON")
            textDanthologyMode.set("Danthology: ON")
            if play_list.REPEAT == 0 : #if Repeat Off -> make Repeat All, because we need some sort of REPEAT for this one.
                play_list.REPEAT = 1
                RepeatButtonText.set("Repeat All")

    def changeTitleTransition(self):
        global play_list
        global Project_Title
        if play_list.usePlayerTitleTransition == True:
            play_list.usePlayerTitleTransition = False
            self.TitleTransitionButtonText.set("Title Transition OFF")
            if play_list.useSongNameTitle:
                Project_Title = "   " + play_list.validFiles[play_list.currentSongIndex].fileName + "   "
                windowCascade.root.title(Project_Title)
            else:
                Project_Title = "   PyPlay MP3 Player in Python     "
                windowCascade.root.title(Project_Title)
        else:
            play_list.usePlayerTitleTransition = True
            self.TitleTransitionButtonText.set("Title Transition ON")
        showCurrentSongInList() #select/highlight the current song in the listbox

    def focus_Input(self, event):
        self.top.wm_attributes("-topmost", 1)
        if self.colorBox.focus_get():
            self.fontBox.focus_force()
        elif self.fontBox.focus_get():
            self.labelColorBox.focus_force()
        elif self.labelColorBox.focus_get():
            self.FontMainColorBox.focus_force()
        elif self.FontMainColorBox.focus_get():
            self.colorBox.focus_force()

    def changeFileNameTransition(self,event):
        global play_list
        global visualSongNameLabel
        play_list.playingFileNameTransition = self.FontTransitionText.get()
        if play_list.playingFileNameTransition == "none":
            visualSongNameLabel = play_list.validFiles[play_list.currentSongIndex].fileName
        elif play_list.playingFileNameTransition == "typewriting":
            visualSongNameLabel = ""
        elif play_list.playingFileNameTransition == "separation":
            visualSongNameLabel = "_" + play_list.validFiles[play_list.currentSongIndex].fileName
        showCurrentSongInList() #select/highlight the current song in the listbox

    def take_focus(self):
        self.top.wm_attributes("-topmost", 1)
        self.top.grab_set()
        self.colorBox.focus_force()

    def browse_background_picture(self):
        global play_list
        background = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(
        ("jpg files", "*.jpg"), ("png files", "*.png"),("gif files", "*.gif"), ("jpeg files", "*.jpeg")))
        if background.endswith(".jpg") or background.endswith(".jpeg") or \
                background.endswith(".png") or background.endswith(".gif"):
            play_list.skin_theme.background_image = background
            img = ImageTk.PhotoImage(Image.open(background))
            background_label.configure(image=img)
            background_label.image = img
        else:
            text = "The background picture has to be one of following formats: .gif, .jpg, .jpeg, .png."
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

#A class to encapsulate into single data object the variables needed to set up a button in WindowDialog
class ButtonFunctionality: #object class used to define Generic Buttons Behaviour
    def __init__(self, text, functionality = None):
        self.Text = text
        self.Functionality = functionality #this field is supposed to be a function

#class defined to describe generic behavior of a dialog window for displaying relevant messages: Warnings / Information
class WindowDialog(Window):
    def __init__(self, textValue=None, Button1_Functionality: ButtonFunctionality = None,
                 Button2_Functionality: ButtonFunctionality = None, windowTitle="Info Box"):
        global allButtonsFont

        self.textValue = textValue
        self.Button1_Func = Button1_Functionality
        self.Button2_Func = Button2_Functionality
        self.windowTitle = windowTitle

        isInfoAlreadyDisplayed = False  # will use this to check whether another window with same content is already displayed

        # Check if there is another a window displaying the same error message:
        for item in windowCascade.WindowDialog:
            if item.textValue == self.textValue and item.windowTitle == self.windowTitle:
                if self.Button1_Func != None and item.Button1_Func != None:
                    if self.Button1_Func.Text == item.Button1_Func.Text and self.Button1_Func.Functionality == item.Button1_Func.Functionality:
                        if self.Button2_Func != None and item.Button2_Func != None:
                            if self.Button2_Func.Text == item.Button2_Func.Text and self.Button2_Func.Functionality == item.Button2_Func.Functionality:
                                isInfoAlreadyDisplayed = True
                        else:
                            isInfoAlreadyDisplayed = True

                else:
                    isInfoAlreadyDisplayed = True

        # For as long as isInfoAlreadyDisplayed will be true it means there is a window displaying same warning/error
        # if user closes it and the problem reappears we will create the window

        if isInfoAlreadyDisplayed == False:
            #if user has too many dialog window opened, close the oldest
            if len(windowCascade.WindowDialog) > 4:
                windowCascade.WindowDialog[0].destroy()
            windowCascade.WindowDialog.append(self)
            self.color = SkinColor.get()
            self.top = tk.Toplevel(windowCascade.root, bg=self.color)
            self.top.protocol("WM_DELETE_WINDOW", self.destroy)
            if self.textValue != None and self.Button1_Func != None:
                self.top.title(self.windowTitle)
                self.top.attributes('-alpha', play_list.windowOpacity)

                # Add scrollbar
                self.verticalScrollBar = ttk.Scrollbar(self.top, orient='vertical')
                self.verticalScrollBar.pack(side=tk.RIGHT, fill='y')

                self.textElement = tk.Text(self.top, fg=labelTextColor, font=allButtonsFont.get(), height=10,
                                           relief=tk.SUNKEN, \
                                           padx=3, pady=3, bg=labelBackground.get(), bd=2,
                                           yscrollcommand=self.verticalScrollBar.set)

                # Add some text in the text widget
                self.textElement.insert(tk.END, self.textValue)
                self.textElement.configure(state=tk.DISABLED)

                # Attach the scrollbar with the text widget
                self.verticalScrollBar.config(command=self.textElement.yview)
                self.textElement.pack(pady=15, padx=15)

                Button1_Command = self.destroy if self.Button1_Func.Functionality == None else Button1_Functionality.Functionality
                Button1 = tk.Button(self.top, text=self.Button1_Func.Text, command=Button1_Command, fg=fontColor.get(),
                                    font=allButtonsFont.get(), bg=self.color)
                if self.Button2_Func != None:
                    Button2_Command = self.destroy if self.Button2_Func.Functionality == None else Button2_Functionality.Functionality
                    Button2 = tk.Button(self.top, text=self.Button2_Func.Text, command=Button2_Command,
                                        fg=fontColor.get(), font=allButtonsFont.get(), bg=self.color)
                    Button2.pack(pady=0, padx=5)
                    Button1.pack(pady=10, padx=5)
                else:
                    Button1.pack(pady=15, padx=15)
                    if self.Button1_Func.Functionality != None: #None is the default command
                        # if only one button passed ensuring after the command is executed we destroy the dialog window
                        def wrapper_func():
                            self.destroy()
                            self.Button1_Func.Functionality()
                        Button1.configure(command=wrapper_func)
                windowSize = (str(self.textElement.winfo_reqwidth() + 50) + "x" + str(
                    self.textElement.winfo_reqheight() + 100) + "+" + str(
                    windowCascade.root.winfo_x() + 100) + "+" + str(windowCascade.root.winfo_y() + 100))
                self.top.geometry(windowSize)
                self.top.bind("<Escape>", self.destroyEsc)
            else:
                self.PredefinedTwoButtonDialogBox()
            if windowTitle == "Information" or windowTitle == "Warning":
                #if important message, take_focus() will bring the window on top of all others
                self.take_focus()  # make window focused
        else:
            # Clean everything - we won't create the window
            del self.textValue
            del self.Button1_Func
            del self.Button2_Func
            del self.windowTitle

    def PredefinedTwoButtonDialogBox(self):
        global allButtonsFont
        Window_Title = "Playlist Dialog"
        self.top.title(Window_Title)
        self.top.geometry(
            "480x200+" + str(windowCascade.root.winfo_x() + 100) + "+" + str(windowCascade.root.winfo_y() + 100))
        self.top.attributes('-alpha', play_list.windowOpacity)
        self.labelInfo = tk.Label(self.top,
                                  text="One song is currently playing.\n\nDo you wish to stop, or keep it in the playlist?", \
                                  fg=fontColor.get(), font=allButtonsFont.get(), bg=self.color).pack()
        StopItButton = tk.Button(self.top, text="Stop It", command=self.stopIt, fg=fontColor.get(),
                                 font=allButtonsFont.get(), bg=self.color)
        KeepItButton = tk.Button(self.top, text="Keep It", command=self.keepCurrentSong, fg=fontColor.get(),
                                 font=allButtonsFont.get(), bg=self.color)
        StopItButton.pack(pady=10)
        KeepItButton.pack(pady=10)
        self.top.bind("<Escape>", self.destroyEsc)

    def destroy(self):
        Window.destroy(self)  # calling parent destructor
        self.top = None
        self.textLabel = None
        self.buttonText = None
        self.windowSize = None
        self.windowTitle = None

    def stopIt(self):
        global play_list
        global listBox_Song_selected_index
        global Project_Title
        if play_list.resetSettings == False:
            play_list.isSongPause = False
            play_list.isSongStopped = False
            play_list.dirFilePath = []
            play_list.validFiles = []
            play_list.currentSongIndex = None
            play_list.currentSongPosition = 0
            play_list.RESUMED = False
            play_list.playTime = 0
            play_list.shufflingHistory = []
            play_list.isListOrdered = 21  # this will mean Custom Sorting
            play_list.PlaylistListenedTime = 0
            play_list.BornDate = datetime.datetime.now()
        else:
            play_list = Playlist()
            # Restore default skin
            play_list.skin_theme.changingSkin()
            windowCascade.root.attributes('-alpha', play_list.windowOpacity)
        stop_music()
        Project_Title = "   PyPlay MP3 Player in Python     "
        windowCascade.root.title(Project_Title)
        self.destroy()
        clearLabels()
        listBox_Song_selected_index = None
        displayElementsOnPlaylist()

    def keepCurrentSong(self):
        global play_list
        global listBox_Song_selected_index
        songToKeep = play_list.validFiles[play_list.currentSongIndex]
        if play_list.resetSettings == False:
            play_list.dirFilePath = []
            play_list.validFiles = []
            play_list.currentSongIndex = 0
            play_list.RESUMED = False
            play_list.playTime = 0
            play_list.shufflingHistory = []
            play_list.isListOrdered = 21  # this will mean Custom Sorting
            play_list.PlaylistListenedTime = 0
            play_list.BornDate = datetime.datetime.now()
        else:
            play_list = Playlist()
            # Restore default skin
            play_list.skin_theme.changingSkin()
            windowCascade.root.attributes('-alpha', play_list.windowOpacity)
        if songToKeep != None:
            play_list.PlaylistListenedTime = songToKeep.SongListenedTime
            play_list.validFiles.append(songToKeep)
            play_list.currentSongIndex = 0
        listBox_Song_selected_index = play_list.currentSongIndex
        del songToKeep
        self.destroy()
        displayElementsOnPlaylist()

#class defined to describe the behavior of a Mp3TagModifier Tool
class Mp3TagModifierTool(Window):
    def __init__(self, fileIndex=0):
        global allButtonsFont
        global rootDirectory
        windowCascade.Mp3TagModifierTool = self
        self.undoRenameBackupFile = rootDirectory +"/backup/RENAMEALLFILES.backup"
        self.undoArtistTitleBackupFile = rootDirectory + "/backup/ALLARTISTTITLE.backup"
        self.undoAlbumYearBackupFile = rootDirectory + "/backup/PREVIOUSALBUMYEAR.backup"
        color = PauseButton["bg"]  # get the color which the rest of elements is using at the moment
        self.top = tk.Toplevel(windowCascade.root, bg=color)
        self.Window_Title = "Mp3TagModifier Tool"
        columnOne=5
        columnTwo = 150
        columnThree = 290

        startingYPos = 5
        verticalSpaceBetweenLabels = 30
        verticalSpaceBetweenButtons = 35
        yPositionForElement = startingYPos

        self.Song = play_list.validFiles[fileIndex]
        self.top.title(self.Window_Title)
        self.top.protocol("WM_DELETE_WINDOW", self.destroy)
        self.top.attributes('-alpha', play_list.windowOpacity)
        tk.Label(self.top, text="File Name:", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnOne, y=yPositionForElement)

        namingCase = tk.Label(self.top, text="Naming Case:", fg=fontColor.get(),
                 font=allButtonsFont.get(), bg=color)
        namingCaseYPos = yPositionForElement
        textConversionValues=["NA","Capitalize", "SemiCapitalize", "Upper Case", "Lower Case"]

        # elements could be placed vertically using positionTkWidgetsVertically instead of recalculating yPositionForElement
        yPositionForElement += verticalSpaceBetweenLabels
        self.NameTag = tk.Entry(self.top, width=70)
        self.NameTag.insert(0, self.Song.fileName)
        self.NameTag.place(x=columnOne, y=yPositionForElement)
        self.NameTag.bind("<Key>", self.setNAOnName)

        formatBoxXPos = int(self.NameTag.place_info()["x"]) + self.NameTag.winfo_reqwidth() + 20
        self.nameTextFormat = StringVar()
        self.nameTextFormat.set("NA")
        self.NameFormatBox = Combobox(self.top, textvariable=self.nameTextFormat,
                values=textConversionValues, width=10, state="readonly", font=allButtonsFont.get())
        self.NameFormatBox.place(x=formatBoxXPos, y=verticalSpaceBetweenLabels)
        namingCase.place(x=formatBoxXPos, y=namingCaseYPos)
        self.NameFormatBox.bind("<<ComboboxSelected>>", self.changeNameFormat)

        yPositionForElement+=verticalSpaceBetweenLabels

        tk.Label(self.top, text="Genre:", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnOne, y=yPositionForElement)
        tk.Label(self.top, text="Year:", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnTwo, y=yPositionForElement)
        tk.Label(self.top, text="Album:", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnThree, y=yPositionForElement)
        taggingCase = tk.Label(self.top, text="Tagging Case:", fg=fontColor.get(),
                 font=allButtonsFont.get(), bg=color)
        taggingCaseYPos = yPositionForElement

        yPositionForElement += verticalSpaceBetweenLabels
        self.GenreTag = tk.Entry(self.top, width=15)
        self.GenreTag.insert(0, self.Song.Genre)
        self.GenreTag.place(x=columnOne, y=yPositionForElement)
        self.GenreTag.bind("<Key>", self.setNAOnTags)

        self.YearTag = tk.Entry(self.top, width=15)
        self.YearTag.insert(0, self.Song.Year)
        self.YearTag.place(x=columnTwo, y=yPositionForElement)
        self.YearTag.bind("<Key>", self.setNAOnTags)

        self.AlbumTag = tk.Entry(self.top, width=30)
        self.AlbumTag.insert(0, self.Song.Album)
        self.AlbumTag.place(x=columnThree, y=yPositionForElement)
        self.AlbumTag.bind("<Key>", self.setNAOnTags)

        self.tagTextFormat = StringVar()
        self.tagTextFormat.set("NA")

        self.TagFormatBox = Combobox(self.top, textvariable=self.tagTextFormat, values=textConversionValues, width=10, state="readonly", font=allButtonsFont.get())
        self.TagFormatBox.place(x=formatBoxXPos, y=yPositionForElement)
        taggingCase.place(x=formatBoxXPos, y=taggingCaseYPos)
        self.TagFormatBox.bind("<<ComboboxSelected>>", self.changeTagFormat)

        yPositionForElement += verticalSpaceBetweenLabels

        tk.Label(self.top, text="Artist:", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color).place(x=columnOne, y=yPositionForElement)
        titleTagLabel = tk.Label(self.top, text="Title:", fg=fontColor.get(), font=allButtonsFont.get(),
                 bg=color)
        titleTagLabelYPos = yPositionForElement

        yPositionForElement += verticalSpaceBetweenLabels
        self.ArtistTag = tk.Entry(self.top, width=35)
        self.ArtistTag.insert(0, self.Song.Artist)
        self.ArtistTag.place(x=columnOne, y=yPositionForElement)
        self.ArtistTag.bind("<Key>", self.setNAOnTags)

        self.TitleTag = tk.Entry(self.top, width=35)
        self.TitleTag.insert(0, self.Song.Title)
        titleTagXPos = int(self.ArtistTag.place_info()["x"]) + self.ArtistTag.winfo_reqwidth() + 20
        self.TitleTag.place(x=titleTagXPos, y=yPositionForElement)
        titleTagLabel.place(x=titleTagXPos, y=titleTagLabelYPos)
        self.TitleTag.bind("<Key>", self.setNAOnTags)

        RemoveCharsButton = tk.Button(self.top, text="Remove Special Characters", command=self.removeChars, fg=fontColor.get(), font=allButtonsFont.get(),
                                bg=color)
        GrabAlbumYearButton = tk.Button(self.top, text="Search Album\Year Tags Online", command=self.grabAlbumAndYear, fg=fontColor.get(), font=allButtonsFont.get(),
                                bg=color)
        SaveChangesButton = tk.Button(self.top, text="Save Changes", command=self.SaveChanges, fg=fontColor.get(), font=allButtonsFont.get(),
                                bg=color)
        ComposeFileNameButton = tk.Button(self.top, text="Set FileName from 'Artist - Title' Tags", command=self.composeFileName, fg=fontColor.get(), font=allButtonsFont.get(),
                                bg=color)
        ComposeArtistTitleButton = tk.Button(self.top, text="Set Artist/Title Tags from FileName", command=self.composeArtistTitle, fg=fontColor.get(), font=allButtonsFont.get(),
                                bg=color)
        self.MassRenameButton = tk.Button(self.top, text="Rename All Files to 'Artist - Title.mp3'", command=self.projection_renameAllFiles, fg=fontColor.get(), font=allButtonsFont.get(),
                                bg=color)
        if play_list.useMassFileEditor:
            self.MassRenameButton.config(state = tk.NORMAL)
        else:
            self.MassRenameButton.config(state = tk.DISABLED)

        self.undoMassRenameButton = tk.Button(self.top, text="Restore Previous FileNames to All Files.", command=self.projection_restorePreviousNames, fg=fontColor.get(), font=allButtonsFont.get(),
                                bg=color)
        if os.path.isfile(self.undoRenameBackupFile) and play_list.useMassFileEditor:
            self.undoMassRenameButton.config(state = tk.NORMAL)
        else:
            self.undoMassRenameButton.config(state = tk.DISABLED)

        self.MassArtistTitleComposeButton = tk.Button(self.top, text="Set Artist/Title Tags from FileName to All Files", command=self.projection_composeArtistTitleAll, fg=fontColor.get(), font=allButtonsFont.get(),
                                bg=color)
        if play_list.useMassFileEditor:
            self.MassArtistTitleComposeButton.config(state = tk.NORMAL)
        else:
            self.MassArtistTitleComposeButton.config(state = tk.DISABLED)

        self.undoMassArtistTitleComposeButton = tk.Button(self.top, text="Restore Previous Artist/Title Tags to All Files", command=self.projection_undoComposeArtistTitleAll, fg=fontColor.get(), font=allButtonsFont.get(),
                               bg=color)
        if play_list.useMassFileEditor and os.path.isfile(self.undoArtistTitleBackupFile):
            self.undoMassArtistTitleComposeButton.config(state = tk.NORMAL)
        else:
            self.undoMassArtistTitleComposeButton.config(state = tk.DISABLED)

        GrabAlbumYearToAll = tk.Button(self.top, text="Search Album\Year Tags Online for All Files", command=self.grabAlbumYearToAllFiles, fg=fontColor.get(), font=allButtonsFont.get(),
                              bg=color)
        if play_list.useMassFileEditor:
            GrabAlbumYearToAll.config(state = tk.NORMAL)
        else:
            GrabAlbumYearToAll.config(state = tk.DISABLED)

        undoAlbumYearToAll = tk.Button(self.top, text="Restore Previous Album/Year Tags to All Files", command=self.projecting_undoEffectsForAlbumYearAllFiles, fg=fontColor.get(), font=allButtonsFont.get(),
                              bg=color)
        if play_list.useMassFileEditor and os.path.exists(self.undoArtistTitleBackupFile):
            undoAlbumYearToAll.config(state = tk.NORMAL)
        else:
            undoAlbumYearToAll.config(state = tk.DISABLED)

        yPositionForElement += verticalSpaceBetweenLabels*1.5
        buttonColumnTwo = columnOne + ComposeFileNameButton.winfo_reqwidth() + 50 #50 will be the margin between the 2 columns
        self.MassRenameButton.place(x=buttonColumnTwo, y=yPositionForElement)
        RemoveCharsButton.place(x=columnOne, y=yPositionForElement)

        yPositionForElement += verticalSpaceBetweenButtons
        self.undoMassRenameButton.place(x=buttonColumnTwo, y=yPositionForElement)
        ComposeFileNameButton.place(x=columnOne, y=yPositionForElement)

        yPositionForElement += verticalSpaceBetweenButtons
        self.MassArtistTitleComposeButton.place(x=buttonColumnTwo, y=yPositionForElement)
        ComposeArtistTitleButton.place(x=columnOne, y=yPositionForElement)

        yPositionForElement += verticalSpaceBetweenButtons
        self.undoMassArtistTitleComposeButton.place(x=buttonColumnTwo, y=yPositionForElement)
        GrabAlbumYearButton.place(x=columnOne, y=yPositionForElement)

        yPositionForElement += verticalSpaceBetweenButtons
        GrabAlbumYearToAll.place(x=buttonColumnTwo, y=yPositionForElement)

        yPositionForElement += verticalSpaceBetweenButtons
        undoAlbumYearToAll.place(x=buttonColumnTwo, y=yPositionForElement)
        SaveChangesButton.place(x=columnOne, y=yPositionForElement)

        self.top.bind("<Tab>", self.focus_out)
        self.top.bind("<Escape>", self.destroyEsc)

        calculateResizeWindow(self.top, [self.MassArtistTitleComposeButton, self.TitleTag,
                                         self.TagFormatBox, SaveChangesButton], 20)



    def projecting_undoEffectsForAlbumYearAllFiles(self):
        try:
            file = open(self.undoAlbumYearBackupFile, "rb")
            dict_list = pickle.load(file)
            file.close()
        except Exception:
            text = ("Exception when loading File: " + str(self.undoArtistTitleBackupFile) +
                    "\nThe content of backup file has been corrupted.")
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle="Warning")
        else:
            messageForUser = ""
            other_available_records = ""

            scheduler.suspend_mainloop()
            for song in play_list.validFiles:
                if scheduler.userIntervention == True:
                    # user changed something in the play_list that might affect the outcome of this loop
                    scheduler.userIntervention = False
                    break
                ttl = "Scanning: " + str(play_list.validFiles.index(song)) + " of " + str(
                    len(play_list.validFiles))
                self.thisWindowTitleUpdate(ttl)
                scheduler.single_loop() # this will make the main window responsive
                for element in dict_list:
                    isSongPlayed = False
                    if self.top == None:  # if window gets closed, terminate
                        return
                    if element['fileName'] == song.fileName:

                        messageForUser += "File: " + song.filePath + "\n\n" + \
                            "Album: '" + song.Album + "' will be changed to: '" + element['oldAlbum'] +"'" +\
                            "\n" +"Year: '" + song.Year + "' will be changed to: '" + element['oldYear'] + "'" + "\n\n"

            scheduler.resume_mainloop()

            if len(dict_list) > 0:
                for element in dict_list:
                    other_available_records += element['fileName'] + "\n"
                other_available_records = "Records available for the following files that are not present " \
                                          "within playlist:\n\n" + other_available_records

            if messageForUser != "":
                text = "Changes to be performed: \n\n" + messageForUser
                text += other_available_records
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("Continue", lambda: self.undoAlbumYearToAllFiles(dict_list)),
                             windowTitle="Restore Previous Album/Year Tags Change Log")
            else:
                text = "No changes can be performed. The backup files hold no previous records for the existing files.\n\n"
                text += other_available_records
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle="Information")

            self.thisWindowTitleUpdate(self.Window_Title)

    def undoAlbumYearToAllFiles(self, dict_list):
        scheduler.suspend_mainloop()
        for song in play_list.validFiles:
            if scheduler.userIntervention == True:
                #user changed something in the play_list that might affect the outcome of this loop
                scheduler.userIntervention = False
                break
            ttl = "Album-Year undoed for: " + str(play_list.validFiles.index(song)) + " of " + str(len(play_list.validFiles))
            self.thisWindowTitleUpdate(ttl)
            scheduler.single_loop() # this will make the main window responsive
            messageForUser = ""
            for element in dict_list:
                isSongPlayed = False
                if self.top == None: #if window gets closed, terminate
                    return
                if element['fileName'] == song.fileName:
                    if pygame.mixer.get_init() and play_list.validFiles.index(song) == play_list.currentSongIndex and pygame.mixer.music.get_busy():
                        if play_list.RESUMED:
                            play_list.currentSongPosition += pygame.mixer.music.get_pos()/1000 #recalculating the resume point of the playback
                        else:
                            play_list.currentSongPosition = pygame.mixer.music.get_pos()/1000
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(clearPlaybackFile) #use this file to release the playback
                        isSongPlayed = True

                    if(os.path.isfile(song.filePath)):
                        mp3file = EasyID3(song.filePath)
                        song.Album = element['oldAlbum']
                        song.Year = element['oldYear']
                        mp3file["album"] = song.Album
                        mp3file["date"] = song.Year
                        if song.Album == "":
                            song.Album = "Various"
                        if song.Year == "":
                            song.Year = "Various"
                        mp3file.save(v2_version=3)
                        del dict_list[dict_list.index(element)]
                        if isSongPlayed:
                            pygame.mixer.music.load(song.filePath)
                            pygame.mixer.music.play()
                            pygame.mixer.music.set_pos(play_list.currentSongPosition)
                            play_list.RESUMED = True
                        break
                    else:
                        messageForUser += "File: \n\n" + song.filePath + " does not exist.\n\n"

        scheduler.resume_mainloop()

        text = "Operation Done.\n\nThe projected changes were performed successfully."
        if messageForUser != "":
            text = "Operation Done.\n\nSome changes could not be performed:\n\n" + messageForUser
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
        self.AlbumTag.delete(0, tk.END)
        self.AlbumTag.insert(0, self.Song.Album)
        self.YearTag.delete(0, tk.END)
        self.YearTag.insert(0, self.Song.Year)
        self.thisWindowTitleUpdate(self.Window_Title)
        file = open(self.undoAlbumYearBackupFile, "wb")
        pickle.dump(dict_list, file)
        file.close()

    def grabAlbumYearToAllFiles(self):
        dictionary={}
        dict_list=[]
        not_found = []
        messageForUser = ""
        dict_loaded=False
        alreadyContained = False
        if os.path.exists(self.undoAlbumYearBackupFile):
            try:
                file = open(self.undoAlbumYearBackupFile, "rb")
                dict_list = pickle.load(file)
            except Exception:
                dict_list = [] #make sure it's empty
                text = ("Exception when loading File: " + str(self.undoAlbumYearBackupFile) +
                        "\nSince the content has been corrupted, your file will be replaced.")
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
            else:
                dict_loaded = True
                file.close()

        scheduler.suspend_mainloop()  # we will keep window refreshed in the loop
        for song in play_list.validFiles:
            if scheduler.userIntervention == True:
                #user changed something in the play_list that might affect the outcome of this loop
                scheduler.userIntervention = False
                break
            scheduler.single_loop() # this will make the main window responsive
            if self.top == None: #if window gets closed, terminate
                return
            dictionary['fileName'] = song.fileName
            dictionary['oldAlbum'] = song.Album if song.Album != "Various" else ""
            dictionary['oldYear'] = song.Year if song.Year != "Various" else ""

            ret_val = self.grabAlbumAndYear(song)
            if ret_val != None:
                not_found.append(ret_val)
            else:
                dictionary['newAlbum'] = song.Album
                dictionary['newYear'] = song.Year

                messageForUser += "File: " + song.filePath + "\n" + \
                    "Album: '" + dictionary['oldAlbum'] + "' changed to: " + dictionary['newAlbum'] + "\n" + \
                    "Year: '" + dictionary['oldYear'] + "' changed to: " + dictionary['newYear'] + "\n\n"

                if dict_loaded:
                    for element in dict_list:
                        if element["fileName"] == song.fileName:
                            dictionary['oldAlbum'] = element["oldAlbum"]
                            dictionary['oldYear'] = element["oldYear"]
                            break
                dict_list.append(dictionary)
            dictionary = {}

        scheduler.resume_mainloop()
        if len(not_found) > 0:
            text = ("Operation Done\n\n" + messageForUser + \
                    "The data for the following items could not be retrieved: \n\n" + "\n".join(not_found))
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None),
                         windowTitle = "Grab Album/Year Tags From Web Change Log")
        else:
            text = "Operation Done\n\nThe data was collected from the Internet. \n\n" +  messageForUser
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

        if len(dict_list) > 0: # we have files changes
            file = open(self.undoAlbumYearBackupFile, "wb")
            pickle.dump(dict_list, file)
            file.close()

    def filterArtistTitleForWebSearch(self, value):
        if value != "Various":
            value = value.replace("'", "")
            value = value.replace(",", "")
            value = value.replace(":", "")
            value = value.replace(".", "")
            value = value.replace("!", "")
            value = value.replace("%", "")
            value = value.replace("?", "")
            value = value.replace("`", "")
            value = value.replace("`", "")
            value = value.replace(" & ", " and ")
            value = value.replace("&", " and ")
            value = value.replace(".mp3", "")
            value = value.replace(".MP3", "")
            value = value.replace(".mP3", "")
            value = value.replace(".Mp3", "")
            value = value.replace(" ", "+")
            return value
        return False

    def filterAlbumFromLastFM(self, data): #this filter might not work anymore in time,
                    #if LastFM decide to change the structure of their webpages.
        text = BeautifulSoup(data, "html.parser")
        text = text.decode("utf-8")
        # Start filtering the html content of the webpage
        if '<div class="source-album-details">' in text:
            text = text.split('<div class="source-album-details">')
            text = text[1].split('</div>')
            text = "".join(text)
            if '<a class' in text:
                text = text.split('<a class')
                text = text[1].split('</a>')
                text = text[0]
                text = text.split(">")
                text = text[1]
                text = "".join(text)
                text = text.strip()
                text = text.strip(" ")
                return text
        return False

    def filterYearFromLastFM(self, data): #this filter might not work anymore in time,
                    #if LastFM decide to change the structure of their webpages.
        text = BeautifulSoup(data, "html.parser")
        text = text.decode("utf-8")
        text = text.replace("\n", "")
        text = text.replace("  ", "")
        # Start filtering the html content of the webpage
        if 'Release Date</dt>' in text:
            text = text.split('Release Date</dt>')
            text = text[1].split('</dd>')
            text = text[0]
            text = text.replace('<dd class="catalogue-metadata-description">', "")
            return text
        return False

    def grabAlbumAndYear(self, song_param=None):
        MassFileEditor = True if type(song_param)==Song else False
        if MassFileEditor == False:
            objectSong = self.Song
        else:
            objectSong = song_param
        urllib3.disable_warnings()
        artist = objectSong.Artist
        artist = self.filterArtistTitleForWebSearch(artist)
        title = objectSong.Title
        title = self.filterArtistTitleForWebSearch(title)
        if artist!= False and title!=False:
            url = "https://www.last.fm/music/" + artist + "/_/" + title # this is possible to change with time. Let's hope it doesn't
            http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=2.0, read=2.0), retries=2)
            if isinstance(song_param, Song) and os.path.isfile(song_param.filePath):
                try:
                    message = "..." if isinstance(song_param, Song) == False else (": " + str(play_list.validFiles.index(song_param)) + " of " + str(len(play_list.validFiles)))
                    self.thisWindowTitleUpdate("Connecting to Last Fm" + message)
                    response = http.request('GET', url)
                except NewConnectionError as exp:  # This is the correct syntax
                    if MassFileEditor==False: #when using MassFileEditor skip this dialogs, because they will be displayed at the end in that function
                        textDialog = ("Unable to establish connection to the server: last.fm" + "\nError Message: " + str(exp)
                        + "\nPlease check your internet connection before proceed.")
                        WindowDialog(textDialog, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
                    return objectSong.fileName + "\nReason: " + str(exp) + "\n"  # return the name of item which was not found on web
                except Exception as exp:
                    if MassFileEditor==False:
                        textDialog = "An exception has been handled. \nI am sorry but I'm unable to retrieve info."
                        WindowDialog(textDialog, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
                    return objectSong.fileName + "\nReason: " + str(exp) + "\n" # return the name of item which was not found on web
                else:
                    if response.status == 200:
                        text = self.filterAlbumFromLastFM(response.data)
                        if text != False:
                            if MassFileEditor == False:
                                self.AlbumTag.delete(0, tk.END)
                                self.AlbumTag.insert(tk.END, text)
                            else:
                                isSongPlayed = False
                                if pygame.mixer.get_init() and play_list.validFiles.index(objectSong) == play_list.currentSongIndex and pygame.mixer.music.get_busy():
                                    if play_list.RESUMED:
                                        play_list.currentSongPosition += pygame.mixer.music.get_pos()/1000 #recalculating the resume point of the playback
                                    else:
                                        play_list.currentSongPosition = pygame.mixer.music.get_pos()/1000
                                    pygame.mixer.music.stop()
                                    pygame.mixer.music.load(clearPlaybackFile) #use this file to release the playback
                                    isSongPlayed = True
                                mp3file = EasyID3(objectSong.filePath)
                                mp3file["album"] = text
                                objectSong.Album = text
                                mp3file.save(v2_version=3)
                                if isSongPlayed:
                                    pygame.mixer.music.load(objectSong.filePath)
                                    pygame.mixer.music.play()
                                    pygame.mixer.music.set_pos(play_list.currentSongPosition)
                                    play_list.RESUMED = True
                                if objectSong == self.Song:
                                    self.AlbumTag.delete(0, tk.END)
                                    self.AlbumTag.insert(tk.END, text)
                            text = text.replace(" ", "+")
                            url = "https://www.last.fm/music/" + artist + "/" + text # this is possible to change with time. Let's hope it doesn't
                            try:
                                response = http.request('GET', url)
                                self.thisWindowTitleUpdate("Looking for Album year release...")
                            except NewConnectionError as exp:  # This is the correct syntax
                                #self.top.title("Error Message: " + str(exp))
                                if MassFileEditor==False:
                                    textDialog = ("Unable to establish connection to the server: last.fm" + "\nError Message: " + str(exp)
                                    + "\nPlease check your internet connection before proceed.")
                                    WindowDialog(textDialog, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
                                else:
                                    return objectSong.fileName + "\nReason: " + str(exp) + "\n"
                            except Exception as exp:
                                if MassFileEditor==False:
                                    textDialog = "An exception has been handled. \nI am sorry but I'm unable to retrieve info."
                                    WindowDialog(textDialog, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
                                else:
                                    return objectSong.fileName + "\nReason: " + str(exp) + "\n"
                            else:
                                if response.status == 200:
                                    text = self.filterYearFromLastFM(response.data)
                                    if text != False:
                                        year = text.split(" ")[len(text.split(" "))-1] # because the I only want to store the year, discard the day and the month.
                                        if MassFileEditor == False:
                                            self.YearTag.delete(0, tk.END)
                                            self.YearTag.insert(tk.END, year)
                                        else:
                                            isSongPlayed = False
                                            if pygame.mixer.get_init() and play_list.validFiles.index(objectSong) == play_list.currentSongIndex and pygame.mixer.music.get_busy():
                                                if play_list.RESUMED:
                                                    play_list.currentSongPosition += pygame.mixer.music.get_pos()/1000 #recalculating the resume point of the playback
                                                else:
                                                    play_list.currentSongPosition = pygame.mixer.music.get_pos()/1000
                                                pygame.mixer.music.stop()
                                                pygame.mixer.music.load(clearPlaybackFile) #use this file to release the playback
                                                isSongPlayed = True
                                            mp3file = EasyID3(objectSong.filePath)
                                            mp3file["date"] = year
                                            objectSong.Year = year
                                            mp3file.save(v2_version=3)
                                            if isSongPlayed:
                                                pygame.mixer.music.load(objectSong.filePath)
                                                pygame.mixer.music.play()
                                                pygame.mixer.music.set_pos(play_list.currentSongPosition)
                                                play_list.RESUMED = True
                                            if objectSong == self.Song:
                                                self.YearTag.delete(0, tk.END)
                                                self.YearTag.insert(tk.END, year)
                                    else:
                                        if MassFileEditor == False:
                                            textDialog = "The year could not be found on Web."
                                            WindowDialog(textDialog, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
                                        else:
                                            return objectSong.fileName + "\nReason: the year could not be found on Web.\n"
                        else:
                            if MassFileEditor == False:
                                textDialog = "There is no webpage available to find the year."
                                WindowDialog(textDialog, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
                            else:
                                self.thisWindowTitleUpdate(self.Window_Title)
                                return objectSong.fileName + "\nReason: there is no webpage available to find the year.\n"
                    else:
                        if MassFileEditor == False:
                            text = "There is no webpage available for this album."
                            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
                        else:
                            self.thisWindowTitleUpdate(self.Window_Title)
                            return objectSong.fileName + "\nReason: there is no webpage available for this album.\n"
            else:
                self.thisWindowTitleUpdate(self.Window_Title)
                return objectSong.fileName + "\nReason: file does not exist.\n" #return the name of item which was not found on web
        else:
            self.thisWindowTitleUpdate(self.Window_Title)
            return objectSong.fileName + " - " + "\nReason: Artist/Title tags are empty or not properly formated.\n"  # return the name of item which was not found on web
        self.thisWindowTitleUpdate(self.Window_Title)
        return None  #File was found.

    def removeSpecialChars(self, originalNameValue):
        originalNameValue = originalNameValue.replace(" & ", " and ")
        originalNameValue = originalNameValue.replace("&", " and ")
        originalNameValue = originalNameValue.replace(" feat. ", " and ")
        originalNameValue = originalNameValue.replace("feat.", " and ")
        originalNameValue = originalNameValue.replace(" vs. ", " and ")
        originalNameValue = originalNameValue.replace(" vs ", " and ")
        originalNameValue = originalNameValue.replace("vs.", " and ")
        originalNameValue = originalNameValue.replace("vs", " and ")
        originalNameValue = originalNameValue.replace(" featuring ", " and ")
        originalNameValue = originalNameValue.replace("+", " plus ")
        originalNameValue = originalNameValue.replace(" + ", " plus ")
        originalNameValue = originalNameValue.replace("%", " percent")
        originalNameValue = originalNameValue.replace(" %", " percent")
        originalNameValue = originalNameValue.replace(" % ", " percent ")
        originalNameValue = originalNameValue.replace("{", "")
        originalNameValue = originalNameValue.replace("}", "")
        originalNameValue = originalNameValue.replace("[", "")
        originalNameValue = originalNameValue.replace("]", "")
        originalNameValue = originalNameValue.replace("|", "")
        originalNameValue = originalNameValue.replace("*", "")
        originalNameValue = originalNameValue.replace("~", "")
        originalNameValue = originalNameValue.replace(". ", "")
        originalNameValue = originalNameValue.replace("=", "")
        originalNameValue = originalNameValue.replace("=", "")
        originalNameValue = originalNameValue.replace(">", "")
        originalNameValue = originalNameValue.replace("<", "")
        originalNameValue = originalNameValue.replace("#", "")
        originalNameValue = originalNameValue.replace("@", "")
        originalNameValue = originalNameValue.replace("`", "'")
        originalNameValue = originalNameValue.replace("^", "")
        originalNameValue = originalNameValue.replace("_", " ")
        originalNameValue = ' '.join(originalNameValue.split()) #remove multiple spaces/tabs
        return originalNameValue

    def removeChars(self):
        originalNameValue = self.NameTag.get()
        self.NameTag.delete(0, tk.END)
        self.NameTag.insert(0, self.removeSpecialChars(originalNameValue))
        originalArtistValue = self.ArtistTag.get()
        self.ArtistTag.delete(0, tk.END)
        self.ArtistTag.insert(0, self.removeSpecialChars(originalArtistValue))
        originalGenreValue = self.GenreTag.get()
        self.GenreTag.delete(0, tk.END)
        self.GenreTag.insert(0, self.removeSpecialChars(originalGenreValue))
        originalTitleValue = self.TitleTag.get()
        self.TitleTag.delete(0, tk.END)
        self.TitleTag.insert(0, self.removeSpecialChars(originalTitleValue))
        originalYearValue = self.YearTag.get()
        self.YearTag.delete(0, tk.END)
        self.YearTag.insert(0, self.removeSpecialChars(originalYearValue))
        originalAlbumValue = self.AlbumTag.get()
        self.AlbumTag.delete(0, tk.END)
        self.AlbumTag.insert(0, self.removeSpecialChars(originalAlbumValue))

    def tagCapitalizer(self):
        if self.ArtistTag.get()!= "Various":
            newValue=self.ArtistTag.get().split(" ")
            value=""
            for word in newValue:
                value+= word.capitalize() + " "
            self.ArtistTag.delete(0, tk.END)
            self.ArtistTag.insert(0, value.strip(" "))
        if self.GenreTag.get()!= "Various":
            newValue=self.GenreTag.get().split(" ")
            value=""
            for word in newValue:
                value+= word.capitalize() + " "
            self.GenreTag.delete(0, tk.END)
            self.GenreTag.insert(0, value.strip(" "))
        if self.TitleTag.get()!= "Various":
            newValue=self.TitleTag.get().split(" ")
            value=""
            for word in newValue:
                value+= word.capitalize() + " "
            self.TitleTag.delete(0, tk.END)
            self.TitleTag.insert(0, value.strip(" "))
        if self.AlbumTag.get()!= "Various":
            newValue=self.AlbumTag.get().split(" ")
            value=""
            for word in newValue:
                value+= word.capitalize() + " "
            self.AlbumTag.delete(0, tk.END)
            self.AlbumTag.insert(0, value.strip(" "))
        if self.YearTag.get()!= "Various":
            newValue=self.YearTag.get().split(" ")
            value=""
            for word in newValue:
                value+= word.capitalize() + " "
            self.YearTag.delete(0, tk.END)
            self.YearTag.insert(0, value.strip(" "))

    def tagSemiCapitalizer(self):
        if self.ArtistTag.get()!= "Various":
            newValue=self.ArtistTag.get().split(" ")
            value=""
            for word in newValue:
                if newValue.index(word) == 0:
                    value+= word.capitalize() + " "
                else:
                    value+= word.lower() + " "
            self.ArtistTag.delete(0, tk.END)
            self.ArtistTag.insert(0, value.strip(" "))
        if self.GenreTag.get()!= "Various":
            newValue=self.GenreTag.get().split(" ")
            value=""
            for word in newValue:
                if newValue.index(word) == 0:
                    value+= word.capitalize() + " "
                else:
                    value+= word.lower() + " "
            self.GenreTag.delete(0, tk.END)
            self.GenreTag.insert(0, value.strip(" "))
        if self.TitleTag.get()!= "Various":
            newValue=self.TitleTag.get().split(" ")
            value=""
            for word in newValue:
                if newValue.index(word) == 0:
                    value+= word.capitalize() + " "
                else:
                    value+= word.lower() + " "
            self.TitleTag.delete(0, tk.END)
            self.TitleTag.insert(0, value.strip(" "))
        if self.AlbumTag.get()!= "Various":
            newValue=self.AlbumTag.get().split(" ")
            value=""
            for word in newValue:
                if newValue.index(word) == 0:
                    value+= word.capitalize() + " "
                else:
                    value+= word.lower() + " "
            self.AlbumTag.delete(0, tk.END)
            self.AlbumTag.insert(0, value.strip(" "))
        if self.YearTag.get()!= "Various":
            newValue=self.YearTag.get().split(" ")
            value=""
            for word in newValue:
                if newValue.index(word) == 0:
                    value+= word.capitalize() + " "
                else:
                    value+= word.lower() + " "
            self.YearTag.delete(0, tk.END)
            self.YearTag.insert(0, value.strip(" "))

    def changeTagFormat(self, event):
        if self.tagTextFormat.get() == "Capitalize":
            self.tagCapitalizer()
        elif self.tagTextFormat.get() == "SemiCapitalize":
            self.tagSemiCapitalizer()
        elif self.tagTextFormat.get() == "Upper Case":
            value = self.ArtistTag.get()
            if value!= "Various":
                self.ArtistTag.delete(0, tk.END)
                self.ArtistTag.insert(0, value.strip(" ").upper())
            value = self.GenreTag.get()
            if value!= "Various":
                self.GenreTag.delete(0, tk.END)
                self.GenreTag.insert(0, value.strip(" ").upper())
            value = self.TitleTag.get()
            if value!= "Various":
                self.TitleTag.delete(0, tk.END)
                self.TitleTag.insert(0, value.strip(" ").upper())
            value = self.AlbumTag.get()
            if value!= "Various":
                self.AlbumTag.delete(0, tk.END)
                self.AlbumTag.insert(0, value.strip(" ").upper())
            value = self.YearTag.get()
            if value!= "Various":
                self.YearTag.delete(0, tk.END)
                self.YearTag.insert(0, value.strip(" ").upper())
        elif self.tagTextFormat.get() == "Lower Case":
            value = self.ArtistTag.get()
            if value!= "Various":
                self.ArtistTag.delete(0, tk.END)
                self.ArtistTag.insert(0, value.strip(" ").lower())
            value = self.GenreTag.get()
            if value!= "Various":
                self.GenreTag.delete(0, tk.END)
                self.GenreTag.insert(0, value.strip(" ").lower())
            value = self.TitleTag.get()
            if value!= "Various":
                self.TitleTag.delete(0, tk.END)
                self.TitleTag.insert(0, value.strip(" ").lower())
            value = self.AlbumTag.get()
            if value!= "Various":
                self.AlbumTag.delete(0, tk.END)
                self.AlbumTag.insert(0, value.strip(" ").lower())
            value = self.YearTag.get()
            if value!= "Various":
                self.YearTag.delete(0, tk.END)
                self.YearTag.insert(0, value.strip(" ").lower())
        showCurrentSongInList() #this will maintain selection

    def setNAOnName(self, event):
        self.nameTextFormat.set("NA")

    def setNAOnTags(self, event):
        self.tagTextFormat.set("NA")

    def changeNameFormat(self, event):
        if self.nameTextFormat.get() == "Capitalize":
            self.NameCapitalizer()
        elif self.nameTextFormat.get() == "SemiCapitalize":
            self.NameSemiCapitalizer()
        elif self.nameTextFormat.get() == "Upper Case":
            value = self.NameTag.get()
            self.NameTag.delete(0, tk.END)
            if value.count("-") == 1:
                value = value.split("-")
                self.NameTag.insert(0, value[0].strip(" ").upper() + " - " + value[1].strip(" ").upper())
            else:
                self.NameTag.insert(0, value.strip(" ").upper())
        elif self.nameTextFormat.get() == "Lower Case":
            value = self.NameTag.get()
            self.NameTag.delete(0, tk.END)
            if value.count("-") == 1:
                value = value.split("-")
                self.NameTag.insert(0, value[0].strip(" ").lower() + " - " + value[1].strip(" ").lower())
            else:
                self.NameTag.insert(0, value.strip(" ").lower())
        showCurrentSongInList() #this will maintain selection.

    def projection_composeArtistTitleAll(self):
        messageForUser = ""
        scheduler.suspend_mainloop()  # we will keep window refreshed in the loop
        for song in play_list.validFiles:
            if scheduler.userIntervention == True:
                #user changed something in the play_list that might affect the outcome of this loop
                scheduler.userIntervention = False
                break
            ttl = "File: " + str(play_list.validFiles.index(song)) + " of " + str(len(play_list.validFiles))
            self.thisWindowTitleUpdate(ttl)
            scheduler.single_loop() # this will make the main window responsive
            if self.top == None: #if window gets closed, terminate
                return
            if song.fileName != "":
                if os.path.exists(song.filePath):
                    if "-" in song.fileName:
                        value = song.fileName
                        value = value.replace(" & ", " and ")
                        value = value.replace("_", " ")
                        value = value.replace("%", " ")
                        value = value.replace("*", " ")
                        value = value.replace("@", " ")
                        value = value.replace("#", " ")
                        value = value.replace("+", " ")
                        value = value.replace("/", " ")
                        value = value.replace("\\", " ")
                        value = value.replace("`", "'")
                        value = value.replace(";", " ")
                        value = value.replace(":", " ")
                        value = value.split("-")
                        #Perform string ethics and formatting for the Artist Name
                        value[0] = value[0].strip(" ")
                        value[0] = [n.capitalize() for n in value[0].split(" ")]
                        value[0] = " ".join(value[0])
                        value[0] = value[0].replace(" And ", " and ")
                        value[0] = value[0].replace(" & ", " and ")
                        value[0] = value[0].replace(" Feat. ", " and ")
                        value[0] = value[0].replace(" Featuring ", " and ")
                        value[0] = value[0].replace(" Feat ", " and ")
                        value[0] = value[0].strip(" ")

                        #Perform string ethics and formatting for the Song Title

                        value[1] = value[1].strip(" ")

                        #this will perform Capitalization and Semi-Capitalization for the Title
                        value[1] = value[1].split(" ")
                        if len(value[1]) > 2:
                            value[1] = [n.capitalize() for n in value[1][:1]] + [n.lower() for n in value[1][1:]]
                        else:
                            value[1] = [n.capitalize() for n in value[1]]
                        value[1] = " ".join(value[1])
                        value[1] = value[1].replace(".mp3", "")
                        value[1] = value[1].strip(" ")

                        artist = song.Artist if song.Artist != "Various" else ""
                        title = song.Title if song.Title != "Various" else ""

                        messageForUser += "File: " + song.fileName + "\n"
                        messageForUser += "Old Artist: '" + artist + "' will be changed to '" + value[0].strip("' ") + "'\n"
                        messageForUser += "Old Title: '" + title + "' will be changed to '" + value[1].strip("' ") + "'\n\n"

                    else:
                        value = song.fileName.lower()
                        value = value.strip(" ")
                        value = value.replace(".mp3", "")

                        messageForUser += "File: " + song.fileName + "\n"
                        messageForUser += "Old Artist: '" + artist + "' will be changed to '" + value + "'\n"
                        messageForUser += "Old Title: '" + title + "' will be changed to ''" + "\n\n"
                else:
                    messageForUser += "No change will be performed to File: " + song.fileName + "\nReason: File does not exist.\n\n"

        scheduler.resume_mainloop()
        self.thisWindowTitleUpdate(self.Window_Title)
        text = "Change Log:\n\n" + messageForUser
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", self.composeArtistTitleAll), windowTitle = "Artist/Title Tag Change Log")

    def composeArtistTitleAll(self):
        dictionary={}
        dict_list=[]
        if os.path.exists(self.undoArtistTitleBackupFile): #enter here if backup file can be found
            try:
                file = open(self.undoArtistTitleBackupFile, "rb")
                dict_list = pickle.load(file)
            except Exception:
                dict_list = [] #make sure it's empty
                text = ("Exception when loading File: " + str(self.undoArtistTitleBackupFile) +
                        "\nSince the content has been corrupted, your file will be replaced.")
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
            else:
                file.close()
            finally:
                file = open(self.undoArtistTitleBackupFile, "wb")
        else:
            file = open(self.undoArtistTitleBackupFile, "wb")

        scheduler.suspend_mainloop() # we will keep window refreshed in the loop
        for song in play_list.validFiles:
            if scheduler.userIntervention == True:
                #user changed something in the play_list that might affect the outcome of this loop
                scheduler.userIntervention = False
                break
            ttl = "Compose Artist-Title: " + str(play_list.validFiles.index(song)) + " of " + str(len(play_list.validFiles))
            self.thisWindowTitleUpdate(ttl)
            scheduler.single_loop() # this will make the main window responsive
            if self.top == None: #if window gets closed, terminate
                return
            if song.fileName != "":
                if os.path.exists(song.filePath):
                    isSongPlayed = False
                    mp3file = EasyID3(song.filePath)
                    ExistingEntry = [Entry for Entry in dict_list if song.fileName in Entry.values()]
                    if len(ExistingEntry) == 0:
                        dictionary['fileName'] = song.fileName
                        if song.Artist!= "Various":
                            dictionary['oldArtist'] = song.Artist
                        else:
                            dictionary['oldArtist'] = ""
                        if song.Title != "Various":
                            dictionary['oldTitle'] = song.Title
                        else:
                            dictionary['oldTitle'] = ""
                    if pygame.mixer.get_init() and play_list.validFiles.index(song) == play_list.currentSongIndex and pygame.mixer.music.get_busy():
                        if play_list.RESUMED:
                            play_list.currentSongPosition += pygame.mixer.music.get_pos()/1000 #recalculating the resume point of the playback
                        else:
                            play_list.currentSongPosition = pygame.mixer.music.get_pos()/1000
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(clearPlaybackFile) #use this file to release the playback
                        isSongPlayed = True
                    if "-" in song.fileName:
                        value = song.fileName
                        value = value.replace(" & ", " and ")
                        value = value.replace("_", " ")
                        value = value.replace("%", " ")
                        value = value.replace("*", " ")
                        value = value.replace("@", " ")
                        value = value.replace("#", " ")
                        value = value.replace("+", " ")
                        value = value.replace("/", " ")
                        value = value.replace("\\", " ")
                        value = value.replace("`", "'")
                        value = value.replace(";", " ")
                        value = value.replace(":", " ")
                        value = value.split("-")
                        #Perform string ethics and formatting for the Artist Name
                        value[0] = value[0].strip(" ")
                        value[0] = [n.capitalize() for n in value[0].split(" ")]
                        value[0] = " ".join(value[0])
                        value[0] = value[0].replace(" And ", " and ")
                        value[0] = value[0].replace(" & ", " and ")
                        value[0] = value[0].replace(" Feat. ", " and ")
                        value[0] = value[0].replace(" Featuring ", " and ")
                        value[0] = value[0].replace(" Feat ", " and ")
                        value[0] = value[0].strip(" ")
                        song.Artist = value[0]
                        #Perform string ethics and formatting for the Song Title

                        value[1] = value[1].strip(" ")

                        #this will perform Capitalization and Semi-Capitalization for the Title
                        value[1] = value[1].split(" ")
                        if len(value[1]) > 2:
                            value[1] = [n.capitalize() for n in value[1][:1]] + [n.lower() for n in value[1][1:]]
                        else:
                            value[1] = [n.capitalize() for n in value[1]]
                        value[1] = " ".join(value[1])
                        value[1] = value[1].replace(".mp3", "")
                        value[1] = value[1].strip(" ")
                        song.Title = value[1].strip(" ")
                        #Set the tags for the mp3 file.
                        mp3file["artist"] = song.Artist
                        mp3file["title"] = song.Title
                        dictionary["newArtist"] = song.Artist
                        dictionary["newTitle"] = song.Title
                    else:
                        value = song.fileName.lower()
                        value = value.strip(" ")
                        value = value.replace(".mp3", "")
                        song.Artist = value
                        mp3file["artist"] = song.Artist
                        dictionary["newArtist"] = song.Artist
                        #Unable to determine the title
                        dictionary["newTitle"] = ""
                    if len(ExistingEntry) == 0:
                        dict_list.append(dictionary)
                    else:
                        dictionary['oldArtist'] = ExistingEntry[0]['oldArtist']
                        dictionary['oldTitle'] = ExistingEntry[0]['oldArtist']
                    mp3file.save(v2_version=3)
                    if isSongPlayed:
                        pygame.mixer.music.load(song.filePath)
                        pygame.mixer.music.play()
                        pygame.mixer.music.set_pos(play_list.currentSongPosition)
                        play_list.RESUMED = True
                    dictionary={}

        scheduler.resume_mainloop()

        self.ArtistTag.delete(0, tk.END)
        self.ArtistTag.insert(0, self.Song.Artist)
        self.TitleTag.delete(0, tk.END)
        self.TitleTag.insert(0, self.Song.Title)
        self.thisWindowTitleUpdate(self.Window_Title)
        text = "Operation Done\n\nArtist/Title tags were changed for all files."
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
        pickle.dump(dict_list, file)
        file.close()
        if os.path.isfile(self.undoArtistTitleBackupFile) and play_list.useMassFileEditor:
            self.undoMassArtistTitleComposeButton.config(state = tk.NORMAL)
        else:
            self.undoMassArtistTitleComposeButton.config(state = tk.DISABLED)

    def projection_undoComposeArtistTitleAll(self):
        dict_list=[]
        messageForUser = ""
        try:
            file = open(self.undoArtistTitleBackupFile, "rb")
            dict_list = pickle.load(file)
            file.close()
        except Exception as exp:
            dict_list = [] #make sure it's empty
            text = ("Backup File Exception:  " + str(exp) +
                    "\nFile: " + str(self.undoArtistTitleBackupFile)+ " might be corrupted.")
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
        else:
            scheduler.suspend_mainloop()  # we will keep window refreshed in the loop
            for song in play_list.validFiles:
                if scheduler.userIntervention == True:
                    # user changed something in the play_list that might affect the outcome of this loop
                    scheduler.userIntervention = False
                    break
                ttl = "File: " + str(play_list.validFiles.index(song)) + " of " + str(len(play_list.validFiles))
                self.thisWindowTitleUpdate(ttl)
                scheduler.single_loop() # this will make the main window responsive
                for element in dict_list:
                    if self.top == None: #if window gets closed, terminate
                        return
                    if element['fileName'] == song.fileName:
                        messageForUser += "File: " + song.fileName + "\nArtist: '" + song.Artist +\
                              "' will be changed to '" + element['oldArtist'] + "'\n" + \
                              "Title: '" + element['oldTitle'] + "' will be changed to: " + element['oldTitle'] +"'\n\n"
                        break

            scheduler.resume_mainloop()
            text = "Change Log: \n\n" + messageForUser
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("Continue", self.undoComposeArtistTitleAll) ,
                         windowTitle = "Restore Previous Artist/Title Tags Change Log")
            self.thisWindowTitleUpdate(self.Window_Title)

    def undoComposeArtistTitleAll(self):
        dict_list=[]
        try:
            file = open(self.undoArtistTitleBackupFile, "rb")
            dict_list = pickle.load(file)
            file.close()
        except Exception as exp:
            dict_list = [] #make sure it's empty
            text = ("Backup File Exception:  " + str(exp) +
                    "\nFile: " + str(self.undoArtistTitleBackupFile)+ " might be corrupted.")
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")

        scheduler.suspend_mainloop() # we will keep window refreshed in the loop
        for song in play_list.validFiles:
            if scheduler.userIntervention == True:
                #user changed something in the play_list that might affect the outcome of this loop
                scheduler.userIntervention = False
                break
            ttl = "Undo composed Artist-Title: " + str(play_list.validFiles.index(song)) + " of " + str(len(play_list.validFiles))
            self.thisWindowTitleUpdate(ttl)
            scheduler.single_loop() # this will make the main window responsive
            for element in dict_list:
                if self.top == None: #if window gets closed, terminate
                    return
                if element['fileName'] == song.fileName:
                    isSongPlayed = False
                    if pygame.mixer.get_init() and play_list.validFiles.index(song) == play_list.currentSongIndex \
                            and pygame.mixer.music.get_busy():
                        if play_list.RESUMED:
                            play_list.currentSongPosition += pygame.mixer.music.get_pos()/1000 #recalculating the resume point of the playback
                        else:
                            play_list.currentSongPosition = pygame.mixer.music.get_pos()/1000
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(clearPlaybackFile) #use this file to release the playback
                        isSongPlayed = True
                    mp3file = EasyID3(song.filePath)
                    song.Artist = element['oldArtist']
                    song.Title = element['oldTitle']
                    mp3file["artist"] = song.Artist
                    mp3file["title"] = song.Title
                    if song.Artist == "":
                        song.Artist = "Various"
                    if song.Title == "":
                        song.Title = "Various"
                    mp3file.save(v2_version=3)
                    del dict_list[dict_list.index(element)]
                    if isSongPlayed:
                        pygame.mixer.music.load(song.filePath)
                        pygame.mixer.music.play()
                        pygame.mixer.music.set_pos(play_list.currentSongPosition)
                        play_list.RESUMED = True
                    break

        scheduler.resume_mainloop()

        if len(dict_list) > 0 :
            message = ""
            for element in dict_list:
                message += element['fileName'] + "\n"
            text = "Previous records also available for following files which are not part of the playlist:\n\n" + message
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
        else:
            text = "Operation Done\n\nPrevious Artist/Title tags have been restored."
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None) , windowTitle = "Information")
        self.ArtistTag.delete(0, tk.END)
        self.ArtistTag.insert(0, self.Song.Artist)
        self.TitleTag.delete(0, tk.END)
        self.TitleTag.insert(0, self.Song.Title)
        self.thisWindowTitleUpdate(self.Window_Title)
        file = open(self.undoArtistTitleBackupFile, "wb")
        pickle.dump(dict_list, file)
        file.close()

    def projection_renameAllFiles(self):
        messageForUser = ""
        scheduler.suspend_mainloop() # we will keep window refreshed in the loop
        for song in play_list.validFiles:
            if scheduler.userIntervention == True:
                #user changed something in the play_list that might affect the outcome of this loop
                scheduler.userIntervention = False
                break
            ttl = "File: " + str(play_list.validFiles.index(song)) + " of " + str(
                len(play_list.validFiles))
            self.thisWindowTitleUpdate(ttl)
            scheduler.single_loop() # this will make the main window responsive
            if self.top == None:  # if the window get closed, terminate the operation
                return
            if song.Artist != "Various" and song.Title != "Various":
                newFileName = song.Artist.strip(" ") + " - " + song.Title.strip(" ") + ".mp3"
                if os.path.exists(song.filePath):
                    messageForUser += "File: " + song.fileName + "\nwill be renamed to:\n" + newFileName +"\n\n"
                else:
                    messageForUser += "File: " + song.fileName + "\nwill NOT be renamed." + "\nReason: File does not exist.\n\n"
            else:
                messageForUser += "File: " + song.fileName + "\nwill NOT be renamed." + "\nReason: Invalid/Empty Artist/Title file tags.\n\n"

        scheduler.resume_mainloop()

        self.thisWindowTitleUpdate(self.Window_Title)
        text = "The files will be renamed as follows: \n\n" +messageForUser
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("Continue", self.renameAllFiles),
                            windowTitle="Renaming Change Log")

    def renameAllFiles(self):
        dictionary = {}
        dict_list = []
        dict_loaded = False
        if os.path.exists(self.undoRenameBackupFile):
            try:
                file = open(self.undoRenameBackupFile, "rb")
                dict_list = pickle.load(file)
            except Exception:
                dict_list = [] #make sure the list is empty now
                text = ("Exception when reading the content of File: " + str(self.undoRenameBackupFile) +
                    "\nSince the content has been corrupted, your file will be replaced.")
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
            else:
                dict_loaded = True
                file.close()
            finally:
                file = open(self.undoRenameBackupFile, "wb")
        else:
            file = open(self.undoRenameBackupFile, "wb")

        scheduler.suspend_mainloop() # we will keep window refreshed in the loop
        for song in play_list.validFiles:
            if scheduler.userIntervention == True:
                #user changed something in the play_list that might affect the outcome of this loop
                scheduler.userIntervention = False
                break
            ttl = "Renamed files: " + str(play_list.validFiles.index(song)) + " of " + str(len(play_list.validFiles))
            self.thisWindowTitleUpdate(ttl)
            scheduler.single_loop() # this will make the main window responsive
            if self.top == None: #if the window get closed, terminate the operation
                return
            if song.Artist != "Various" and song.Title != "Various":
                newFileName = song.Artist.strip(" ") + " - " + song.Title.strip(" ") + ".mp3"
                pathToFile = song.filePath.split(song.fileName)
                pathToFile = pathToFile[0]
                alreadyContained = False
                if dict_loaded:
                    for element in dict_list:
                        if element['newName'] == pathToFile + newFileName and song.fileName == newFileName:
                            alreadyContained = True
                            break
                if alreadyContained == False and os.path.exists(song.filePath):
                    dictionary['oldName'] = song.filePath
                    dictionary['newName'] = pathToFile + newFileName
                    dict_list.append(dictionary)
                    dictionary = {}
                    try:
                        isSongPlayed = False
                        if pygame.mixer.get_init():
                            if play_list.validFiles.index(song) == play_list.currentSongIndex and \
                            pygame.mixer.music.get_busy():  # enter here if the file to be renamed is currently playing
                                if play_list.RESUMED:
                                    play_list.currentSongPosition += pygame.mixer.music.get_pos()/1000 #recalculating the resume point of the playback
                                else:
                                    play_list.currentSongPosition = pygame.mixer.music.get_pos()/1000
                                pygame.mixer.music.stop()
                                pygame.mixer.music.load(clearPlaybackFile) #use this file to release the playback
                                isSongPlayed = True
                        os.rename(song.filePath, pathToFile + newFileName)  # this will rename the file
                        song.fileName = newFileName  # this will update the play_list with the new song info
                        song.filePath = pathToFile + newFileName
                        if isSongPlayed:
                            pygame.mixer.music.load(song.filePath)
                            pygame.mixer.music.play()
                            pygame.mixer.music.set_pos(play_list.currentSongPosition)
                            play_list.RESUMED = True
                    except Exception as Exp:
                        text = ("Exception during Mass Rename: " + str(Exp))
                        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")

        scheduler.resume_mainloop()

        displayElementsOnPlaylist()
        showCurrentSongInList()
        self.NameTag.delete(0, tk.END)
        self.NameTag.insert(0, self.Song.fileName)
        pickle.dump(dict_list, file)
        file.close()
        self.thisWindowTitleUpdate(self.Window_Title)
        text = "Operation Done\n\nAll files were renamed."
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
        if os.path.isfile(self.undoRenameBackupFile) and play_list.useMassFileEditor:
            self.undoMassRenameButton.config(state=tk.NORMAL)
        else:
            self.undoMassRenameButton.config(state=tk.DISABLED)

    def projection_restorePreviousNames (self):
        global play_list
        dict_list=[]
        messageForUser = ""
        try:
            file = open(self.undoRenameBackupFile, "rb")
            dict_list = pickle.load(file)
            file.close()
        except Exception as exp:
            dict_list = [] #make sure it's empty
            text = ("Backup File Exception: " + exp
                    +"\nFile: " + str(self.undoRenameBackupFile)+ " might be corrupted.")
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")

        scheduler.suspend_mainloop()  # we will keep window refreshed in the loop
        for song in play_list.validFiles:
            if scheduler.userIntervention == True:
                #user changed something in the play_list that might affect the outcome of this loop
                scheduler.userIntervention = False
                break
            ttl = "File: " + str(play_list.validFiles.index(song)) + " of " + str(len(play_list.validFiles))
            self.thisWindowTitleUpdate(ttl)
            scheduler.single_loop() # this will make the main window responsive
            for element in dict_list:
                if self.top == None: #if window gets closed, terminate
                    return
                if element['newName'] == song.filePath:
                    filePath = element['newName'].split(song.fileName)
                    filePath = filePath[0]
                    FileName = element['oldName'].split(filePath)
                    FileName = FileName[1]
                    messageForUser += "File: " + song.fileName + "\nwill be renamed to:\n" + FileName + "\n\n"
                    break
                if dict_list.index(element) == len(dict_list)-1 and element['newName'] != song.filePath:
                    messageForUser += "File: " + song.fileName + "\nwill not be changed.\nReason: " \
                                                                 "No records stored in the backup.\n\n"

        scheduler.resume_mainloop()

        self.thisWindowTitleUpdate(self.Window_Title)
        text = "Change Log: \n\n" + messageForUser
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("Continue", self.restorePreviousNames),
                     windowTitle = "Restore Previous Names Change Log")

    def restorePreviousNames (self):
        global play_list
        dict_list=[]
        message = ""
        try:
            file = open(self.undoRenameBackupFile, "rb")
            dict_list = pickle.load(file)
            file.close()
        except Exception as exp:
            dict_list = [] #make sure it's empty
            text = ("Backup File Exception: " + exp
                    +"\nFile: " + str(self.undoRenameBackupFile)+ " might be corrupted.")
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")

        scheduler.suspend_mainloop()  # we will keep window refreshed in the loop
        for song in play_list.validFiles:
            if scheduler.userIntervention == True:
                #user changed something in the play_list that might affect the outcome of this loop
                scheduler.userIntervention = False
                break
            ttl = "Restored previous names: " + str(play_list.validFiles.index(song)) + " of " + str(len(play_list.validFiles))
            self.thisWindowTitleUpdate(ttl)
            scheduler.single_loop() # this will make the main window responsive
            for element in dict_list:
                if self.top == None: #if window gets closed, terminate
                    return
                if element['newName'] == song.filePath:
                    filePath = element['newName'].split(song.fileName)
                    filePath = filePath[0]
                    FileName = element['oldName'].split(filePath)
                    FileName = FileName[1]
                    try:
                        isSongPlayed = False
                        if pygame.mixer.get_init() and play_list.validFiles.index(song) == \
                                        play_list.currentSongIndex and pygame.mixer.music.get_busy():  # enter here if the file to be renamed is currently playing
                            play_list.isSongPause = True
                            if play_list.RESUMED:
                                play_list.currentSongPosition += pygame.mixer.music.get_pos()/1000 #recalculating the resume point of the playback
                            else:
                                play_list.currentSongPosition = pygame.mixer.music.get_pos()/1000
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(clearPlaybackFile)  # clear the playback
                            isSongPlayed = True
                        os.rename(song.filePath, element['oldName'])  # this will rename the file
                        song.fileName = FileName  # this will update the play_list with the new song info
                        song.filePath = element['oldName']
                        if isSongPlayed:
                            pygame.mixer.music.load(song.filePath)
                            pygame.mixer.music.play()
                            pygame.mixer.music.set_pos(play_list.currentSongPosition)
                            play_list.RESUMED = True
                    except Exception as Exp:
                        text = ("Exception during Undo Mass Rename: " + str(Exp))
                        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
                    del dict_list[dict_list.index(element)]
                    break
                if dict_list.index(element) == len(dict_list)-1 and element['newName'] != song.filePath:
                    message += song.fileName + "\n"

        scheduler.resume_mainloop()

        displayElementsOnPlaylist()
        showCurrentSongInList()
        self.NameTag.delete(0, tk.END)
        self.NameTag.insert(0, self.Song.fileName)
        file = open(self.undoRenameBackupFile, "wb")
        pickle.dump(dict_list, file)
        file.close()
        self.thisWindowTitleUpdate(self.Window_Title)
        if message!="":
            text = "Some file were not renamed: \n" + message
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
        else:
            text = "Operation Done\n\nPrevious names have been restored to all files."
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

    def NameCapitalizer(self):
        if "-" in self.NameTag.get():
            value = self.NameTag.get()
            value = value.split("-")
            artist = ""
            title = ""
            for word in value[0].split(" "):
                artist += word.capitalize() + " "
            for word in value[1].split(" "):
                if value[1].split(" ").index(word) < len(value[1].split(" "))-1:
                    title += word.capitalize() + " "
                else:
                    title += word.capitalize()

            if len(value) > 2:
                title+=" "
                for i in range(2, len(value)):
                    title+= value[i].capitalize() + " "
            title = title.strip(" ")  # remove the last blank space
            artist = artist.strip(" ")
            if title.lower().endswith(".mp3"):
                value = artist + " - " + title
            else:
                value = artist + " - " + title + ".mp3"
            self.NameTag.delete(0, tk.END)
            self.NameTag.insert(0, value)
        else:
            value = self.NameTag.get()
            value = value.split(" ")
            newValue = ""
            for element in value:
                newValue += element.strip(" ").capitalize() + " "
            self.NameTag.delete(0, tk.END)
            self.NameTag.insert(0, newValue.rstrip(" "))

    def composeArtistTitle(self):
        if self.NameTag.get() != "":
            if "-" in self.NameTag.get():
                value = self.NameTag.get()
                value = value.split("-")
                value[0] = value[0].strip(" ")
                value[0] = [n.capitalize() for n in value[0].split(" ")] #perform Capitalization for Artist Name
                self.ArtistTag.delete(0,tk.END)
                value[0] = " ".join(value[0])
                value[0] = value[0].strip(" ")
                value[0] = value[0].replace("And", "and")
                self.ArtistTag.insert(0, value[0])
                self.TitleTag.delete(0, tk.END)
                value[1] = value[1].replace(".mp3", "")
                value[1] = value[1].replace(".MP3", "")
                value[1] = value[1].replace(".Mp3", "")
                value[1] = value[1].replace(".mP3", "")
                value[1] = value[1].strip(" ")
                ##this will perform Capitalization and Semi-Capitalization for the Title
                if len(value[1].split(" ")) > 2:
                    val = value[1][0].capitalize() + value[1][1:].lower()
                    self.TitleTag.insert(0, val)
                else:
                    value[1] = [n.capitalize() for n in value[1].split(" ")]
                    value[1] = " ".join(value[1])
                    self.TitleTag.insert(0, value[1].strip(" "))
            else:
                self.ArtistTag.delete(0, tk.END)
                value = self.NameTag.get().replace(".mp3", "")
                value = value.replace(".mP3", "")
                value = value.replace(".Mp3", "")
                value = value.replace(".MP3", "")
                value = value.replace("And", "and")
                value = value.strip(" ")
                self.ArtistTag.insert(0, value)
        else:
            text = "The name should not be empty."
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

    def composeFileName(self):
        if self.ArtistTag.get() != "Various" and self.TitleTag.get() != "Various":
            self.NameTag.delete(0,tk.END)
            self.NameTag.insert(0, self.ArtistTag.get() + " - " + self.TitleTag.get())
        else:
            text = "The Artist Name nor the Title should be 'Various'."
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

    def NameSemiCapitalizer(self):
        if "-" in self.NameTag.get():
            value = self.NameTag.get()
            value = value.split("-")
            artist = ""
            title = ""
            value[0] = value[0].strip(" ")
            for word in value[0].split(" "):
                artist += word.capitalize() + " "
            value[1] = value[1].strip(" ")
            for word in value[1].split(" "):
                if value[1].split(" ").index(word) == 0:
                    title = word.capitalize() + " "
                else:
                    title += word.lower() + " "

            if len(value) > 2:
                for i in range(2, len(value)):
                    title+= value[i].lower() + " "
            title = title.strip(" ") #remove the last blank space
            artist = artist.strip(" ")
            if title.lower().endswith(".mp3"):
                value = artist + " - " +title
            else:
                value = artist + " - " + title + ".mp3"
            self.NameTag.delete(0, tk.END)
            self.NameTag.insert(0, value)
        else:
            value = self.NameTag.get()
            value = value.capitalize()
            self.NameTag.delete(0, tk.END)
            self.NameTag.insert(0, value)

    def SaveChanges(self):
        global play_list
        pathToFile = self.Song.filePath.split(self.Song.fileName)
        pathToFile = pathToFile[0]
        index = play_list.validFiles.index(self.Song)
        if self.NameTag.get().lower().endswith(".mp3") == False:
            value = self.NameTag.get()
            self.NameTag = StringVar()
            self.NameTag.set(value + ".mp3")
        try:
            if pygame.mixer.get_init() and index == play_list.currentSongIndex and pygame.mixer.music.get_busy(): # enter here if the file to be renamed is currently playing
                if play_list.RESUMED:
                    play_list.currentSongPosition = math.floor(play_list.currentSongPosition + pygame.mixer.music.get_pos() / 1000)
                else:
                    play_list.currentSongPosition = math.floor(pygame.mixer.music.get_pos()/1000)
                pygame.mixer.music.stop()
                if self.Song.filePath.lower() != (pathToFile+self.NameTag.get()).lower():
                    shutil.copy(self.Song.filePath, pathToFile+self.NameTag.get())
                    fileToRemove = self.Song.filePath
                    self.Song.fileName = self.NameTag.get()  # this will update the play_list with the new song info
                    self.Song.filePath = pathToFile + self.NameTag.get()
                    self.saveMp3Tags()
                    del play_list.validFiles[play_list.currentSongIndex]
                    play_list.validFiles.insert(play_list.currentSongIndex, self.Song)
                    displayElementsOnPlaylist()
                    showCurrentSongInList()
                    pygame.mixer.music.load(play_list.validFiles[play_list.currentSongIndex].filePath) #release the old file, to be able to remove it
                    os.remove(fileToRemove)  # remove the old one
                    play_music() #load the new file in the player, so that the old one gets released
                    # play_music() function should always be called last.
                    # As this function triggers a scheduler which will only end during pause or stop
                    # statements placed ater play_music will not be executed until scheduler ends which
                    # produces huge delays in their execution
                else: #will enter here is used Capitalize Filename Option
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(clearPlaybackFile) #use this file to release the playback
                    if self.Song.filePath != pathToFile + self.NameTag.get():
                        os.rename(self.Song.filePath, pathToFile + self.NameTag.get())  # this will rename the file
                        self.Song.fileName = self.NameTag.get()  # this will update the play_list with the new song info
                        self.Song.filePath = pathToFile + self.NameTag.get()
                    self.saveMp3Tags()
                    pygame.mixer.music.load(self.Song.filePath)
                    displayElementsOnPlaylist()
                    showCurrentSongInList()
                    play_music()
                    # play_music() function should always be called last.
                    # As this function triggers a scheduler which will only end during pause or stop
                    # statements placed ater play_music will not be executed until scheduler ends which
                    # produces huge delays in their execution
            else:
                if self.Song.filePath != (pathToFile + self.NameTag.get()):
                    os.rename(self.Song.filePath, pathToFile + self.NameTag.get()) #this will rename the file
                    self.Song.fileName = self.NameTag.get() # this will update the play_list with the new song info
                    self.Song.filePath = pathToFile + self.NameTag.get()
                self.saveMp3Tags()
                displayElementsOnPlaylist()
                showCurrentSongInList()
        except Exception as Exp:
            text = ("Exception during File Tag Update: " + str(Exp))
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")

    def saveMp3Tags(self):
        mp3file = EasyID3(self.Song.filePath)
        if self.GenreTag.get() != "Various":
            mp3file["genre"] = self.GenreTag.get()
            self.Song.Genre = mp3file["genre"]
            self.Song.Genre = self.Song.Genre[0]
        if self.ArtistTag.get() != "Various":
            mp3file["artist"] = self.ArtistTag.get()
            self.Song.Artist = mp3file["artist"]
            self.Song.Artist = self.Song.Artist[0]
        if self.AlbumTag.get() != "Various":
            mp3file["album"] = self.AlbumTag.get()
            self.Song.Album = mp3file["album"]
            self.Song.Album = self.Song.Album[0]
        if self.YearTag.get() != "Various":
            mp3file["date"] = self.YearTag.get()
            self.Song.Year = mp3file["date"]
            self.Song.Year = self.Song.Year[0]
        if self.TitleTag.get() != "Various":
            mp3file["title"] = self.TitleTag.get()
            self.Song.Title = mp3file["title"]
            self.Song.Title = self.Song.Title[0]
        mp3file.save(v2_version=3)

    def take_focus(self):
        self.top.wm_attributes("-topmost", 1)
        self.top.grab_set()
        self.NameTag.focus_force()

#class defined to describe the behavior of a web-crawler set up to look for lyrics of specified song within the playlist
class GrabLyricsTool(Window):
    def __init__(self, index="empty"):
        global allButtonsFont
        self.LyricsDownloads = rootDirectory + "/backup/LyricsDownloads.lyl"
        if index=="empty":
            index = play_list.currentSongIndex # do not forget that currentSongIndex can be None
        self.songIndex = index
        if self.songIndex != None: # make sure there is a song to search lyrics for.
            windowCascade.GrabLyricsTool = self
            color = PauseButton["bg"]  # get the color which the rest of elements is using at the moment
            self.top = tk.Toplevel(bg=color)
            self.Window_Title = "Grab Lyrics Tool"
            self.top.title(self.Window_Title)
            self.top.geometry("580x550+" + str(windowCascade.root.winfo_x()+100) + "+" + str(windowCascade.root.winfo_y()+100))
            self.top.protocol("WM_DELETE_WINDOW", self.destroy)
            self.top.attributes('-alpha', play_list.windowOpacity)

            self.welcomeMessage = StringVar()
            self.welcomeMessage.set("Welcome to Grab Lyrics Tool!\n\nThe lyrics are grabbed from various online sources,\n" \
                                +"the results are provided according to your internet connection speed.\n" \
                                +"The Search is based on Artist - Title tags, if these tags are not set\n" \
                                +"accordingly, the lyrics will never be found.")
            self.welcomingLabel = tk.Label(self.top, textvariable=self.welcomeMessage, fg=fontColor.get(), font=allButtonsFont.get(), bg=color,anchor="e", justify=tk.LEFT)
            self.welcomingLabel.place(x=30, y=5)

            self.Lyrics = StringVar()
            self.Lyrics.set("Lyrics")
            self.LabelSelectedFile = tk.Label(self.top, textvariable=self.Lyrics, fg=fontColor.get(), font=allButtonsFont.get(), bg=color)
            self.LabelSelectedFile["wraplength"] = self.welcomingLabel.winfo_reqwidth()
            self.LabelSelectedFile.place(x=30, y=115)

            self.frame = tk.Frame(self.top, width=500, height=30, bg=color, borderwidth=1)
            positionTkWidgetsVertically(10, self.LabelSelectedFile, self.frame, 30)

            self.scrlbar = ttk.Scrollbar(self.frame, orient="vertical")
            self.listboxLyrics = tk.Listbox(self.frame, fg=fontColor.get(), font=allButtonsFont.get(), width=65, bg=color, height=20, relief=tk.GROOVE, \
                         yscrollcommand=self.scrlbar.set, borderwidth=2, selectbackground = fontColor.get(), selectforeground = color)
            self.listboxLyrics.pack(padx=10, pady=10, side = tk.LEFT)
            self.listboxLyrics.bind('<ButtonPress-3>', self.rightClickOnLyrics)
            self.scrlbar.config(command=self.listboxLyrics.yview)
            self.scrlbar.pack(side=tk.RIGHT, fill=tk.Y)

            #Preparing parties for resizing window to fit content and element vertical placement
            self.frame["width"] = self.listboxLyrics.winfo_reqwidth() + self.scrlbar.winfo_reqwidth()
            self.frame["height"] = self.listboxLyrics.winfo_reqheight()

            self.SaveLyrics = tk.Button(self.top, text="Save Lyrics",command=self.saveLyrics, fg=fontColor.get(), font=allButtonsFont.get(),
                                              bg=color, state=tk.DISABLED)

            positionTkWidgetsVertically(20, self.frame, self.SaveLyrics, 30)

            self.RemoveLyrics = tk.Button(self.top, text="Remove Lyrics", command=self.removeLyrics, fg=fontColor.get(),
                                        font=allButtonsFont.get(),
                                        bg=color, state=tk.DISABLED)
            self.RemoveLyrics.place(x=130, y=self.SaveLyrics.place_info()["y"])

            self.DownloadLyricsAll = tk.Button(self.top, text="Download All Lyrics", command=self.downloadAllLyrics, fg=fontColor.get(),
                                          font=allButtonsFont.get(),
                                          bg=color)
            self.DownloadLyricsAll.place(x=260, y=self.SaveLyrics.place_info()["y"])
            self.top.bind("<Tab>", self.focus_out)
            self.top.bind("<Escape>", self.destroyEsc)
            if os.path.exists(self.LyricsDownloads):
                try:
                    file = open(self.LyricsDownloads, "rb")
                    lyricsList = pickle.load(file)
                    file.close()
                    for element in lyricsList:
                        if element["fileName"] == play_list.validFiles[self.songIndex].fileName:
                            for line in element["lyrics_list"]:
                                self.listboxLyrics.insert(tk.END, line)
                            self.Lyrics.set("Lyrics for '" + play_list.validFiles[self.songIndex].Artist + " - " \
                                            + play_list.validFiles[self.songIndex].Title + "' -> were found locally:")
                            self.RemoveLyrics.config(state=tk.NORMAL)
                            break
                    if self.listboxLyrics.size() == 0: #lyrics not found.
                        self.LyricsDisplay()
                except Exception:
                    text = ("Could not load the file: " + self.LyricsDownloads +
                            "\nI will search for lyrics online.")
                    WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
                    self.LyricsDisplay()
            else:
                self.LyricsDisplay()

            calculateResizeWindow(self.top, [self.frame, self.LabelSelectedFile, self.welcomingLabel, self.SaveLyrics], 30)
        else:
            WindowDialog("Playlist is empty.", Button1_Functionality=ButtonFunctionality("OK", None),
                         windowTitle="Grab Lyrics Tool")
    def downloadAllLyrics(self):
        message = ""

        scheduler.suspend_mainloop()  # we will keep window refreshed in the loop
        for i in range(0, len(play_list.validFiles)):
            if self.top == None:
                return
            if scheduler.userIntervention == True:
                #user changed something in the play_list that might affect the outcome of this loop
                scheduler.userIntervention = False
                break
            ttl = "Searched lyrics for: " + str(i) + " of " + str(len(play_list.validFiles))
            self.thisWindowTitleUpdate(ttl)
            scheduler.single_loop() # this will make the main window responsive
            self.songIndex = i
            text_list, source = self.accessPage()
            if len(text_list) > 0 and source != "":
                self.saveLyrics(text_list)
            else:
                message += play_list.validFiles[i].fileName + "\n"

        scheduler.resume_mainloop()
        self.thisWindowTitleUpdate(self.Window_Title)
        if message!="":
            text = ("Lyrics not found for: " + str(message.count("\n")) + " songs \n\n" + message)
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

    def removeLyrics(self):
        filename = play_list.validFiles[self.songIndex].fileName
        lyrics_dictionary = {}
        lyricsList = []
        if os.path.exists(self.LyricsDownloads):
            try:
                file = open(self.LyricsDownloads, "rb")
                lyricsList = pickle.load(file)
                file.close()
            except Exception:
                text = ("Could not load the file: " + self.LyricsDownloads)
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
        if len(lyricsList) > 0:
            for element in lyricsList:
                if element["fileName"] == filename:
                    del lyricsList[lyricsList.index(element)]
                    text = "The lyrics for this song were removed."
                    WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
                    break
            try:
                file = open(self.LyricsDownloads, "wb")
                pickle.dump(lyricsList, file)
                file.close()
                self.RemoveLyrics.config(state=tk.DISABLED)
                self.SaveLyrics.config(state=tk.NORMAL)
            except Exception:
                text = ("Could not remove Lyrics for: " + filename)
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")

    def saveLyrics(self, list_text=None):
        filename = play_list.validFiles[self.songIndex].fileName
        lyrics_dictionary = {}
        lyricsList = []
        if os.path.exists(self.LyricsDownloads):
            try:
                file = open(self.LyricsDownloads, "rb")
                lyricsList = pickle.load(file)
                file.close()
            except Exception:
                if list_text==None: #skip the messages, we have work to do, the lyrics are being downloaded for the entire playlist.
                    text = ("Could not load the file: " + self.LyricsDownloads)
                    WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
        alreadyContained = False
        if len(lyricsList) > 0:
            for element in lyricsList:
                if element["fileName"] == filename:
                    alreadyContained = True
                    if list_text==None: #skip the messages, we have work to do, the lyrics are being downloaded for the entire playlist.
                        text = "This lyrics are already stored in your local computer."
                        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
                    break
        if alreadyContained == False:
            lyrics_dictionary["fileName"] = filename
            if list_text == None:
                lyrics_dictionary["lyrics_list"] = list(self.listboxLyrics.get(0,tk.END))
            else:
                lyrics_dictionary["lyrics_list"] = list_text
            lyricsList.append(lyrics_dictionary)
            lyrics_dictionary={}
            del lyrics_dictionary
            try:
                file = open(self.LyricsDownloads, "wb")
                pickle.dump(lyricsList, file)
                file.close()
                self.RemoveLyrics.config(state=tk.NORMAL)
                self.SaveLyrics.config(state=tk.DISABLED)
                if list_text==None: #skip the messages, we have work to do, the lyrics are being downloaded for the entire playlist.
                    text = "The lyrics for this song were saved."
                    WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
            except Exception:
                if list_text==None:
                    text = ("Could not save Lyrics for: " + filename)
                    WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")

    def accessPage(self):
        urllib3.disable_warnings()
        text_list = []
        source = ""
        if play_list.validFiles[self.songIndex].Artist != "Various" and play_list.validFiles[
            self.songIndex].Title != "Various":
            artist = play_list.validFiles[self.songIndex].Artist
            artist = artist.replace("'", "")
            artist = artist.replace(",", "")
            artist = artist.replace(":", "")
            artist = artist.replace(".", "")
            artist = artist.replace("!", "")
            artist = artist.replace("%", "")
            artist = artist.replace("?", "")
            artist = artist.replace("`", "")
            artist = artist.replace("`", "")
            artist = artist.replace(" & ", " and ")
            artist = artist.replace("&", " and ")
            artist = artist.replace(" ", "-")
            title = play_list.validFiles[self.songIndex].Title
            title = title.replace("'", "")
            title = title.replace(",", "")
            title = title.replace(":", "")
            title = title.replace(".", "")
            title = title.replace("!", "")
            title = title.replace("%", "")
            title = title.replace("?", "")
            title = title.replace("`", "")
            title = title.replace("&", "")
            title = title.replace(".mp3", "")
            title = title.replace(".MP3", "")
            title = title.replace(".mP3", "")
            title = title.replace(".Mp3", "")
            title = title.replace(" ", "-")
            if play_list.LyricsActiveSource == "lyrics.my" or (play_list.LyricsActiveSource == "all" and len(text_list)==0):
                url = "http://www.lyrics.my/artists/" + artist + "/lyrics/" + title  # this is possible to change with time. Let's hope it doesn't
                http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=2.0, read=2.0), retries=1)
                try:
                    response = http.request('GET', url)
                except NewConnectionError as exp:    # This is the correct syntax
                    windowCascade.root.title("Unable to establish connection to" + str(LyricsOnlineSources[2]) + " for: " + artist + " - " + title)
                except Exception:
                    windowCascade.root.title("Unable to retrieve lyrics for: " + artist + " - " + title + " from " + str(LyricsOnlineSources[2]))
                else:
                    if response.status == 200:
                        text_list = self.filterTextFromLyricsMy(response.data)
                        source = "lyrics.my"
            if play_list.LyricsActiveSource == "genius.com" or (play_list.LyricsActiveSource == "all" and len(text_list)==0):
                url = "https://genius.com/" + artist + "-" + title + "-lyrics"  # this is possible to change with time. Let's hope it doesn't
                # The URL system for genius.com is structured like this at the moment.
                http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=2.0, read=2.0), retries=1)
                try:
                    response = http.request('GET', url)
                except NewConnectionError as exp:    # This is the correct syntax
                    windowCascade.root.title("Unable to establish connection to" + str(LyricsOnlineSources[1]) + " for: " + artist + " - " + title)
                except Exception:
                    windowCascade.root.title("Unable to retrieve lyrics for: " + artist + " - " + title + " from " + str(LyricsOnlineSources[1]))
                else:
                    if response.status == 200:
                        text_list = self.filterTextFromGeniusCom(response.data)
                        source = "genius.com"
            if play_list.LyricsActiveSource == "lyricsmix.net" or (play_list.LyricsActiveSource == "all" and len(text_list)==0):
                url = "https://lyricsmix.net/" + artist + "-" + title + "-lyrics/"  # this is possible to change with time. Let's hope it doesn't
                http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=2.0, read=2.0), retries=1)
                try:
                    response = http.request('GET', url)
                except NewConnectionError as exp:    # This is the correct syntax
                    windowCascade.root.title("Unable to establish connection to" + str(LyricsOnlineSources[3]) + " for: " + artist + " - " + title)
                except Exception:
                    windowCascade.root.title("Unable to retrieve lyrics for: " + artist + " - " + title + " from " + str(LyricsOnlineSources[3]))
                else:
                    if response.status == 200:
                        text_list = self.filterTextFromLyricsMixNet(response.data)
                        source = "lyricsmix.net"
            if play_list.LyricsActiveSource == "omnialyrics.it" or (play_list.LyricsActiveSource == "all" and len(text_list)==0):
                url = "https://omnialyrics.it/" + title + "-testo-" + artist +"/"  # this is possible to change with time. Let's hope it doesn't
                http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=2.0, read=2.0), retries=1)
                try:
                    response = http.request('GET', url)
                except NewConnectionError as exp:    # This is the correct syntax
                    windowCascade.root.title("Unable to establish connection to" + str(LyricsOnlineSources[4]) + " for: " + artist + " - " + title)
                except Exception:
                    windowCascade.root.title("Unable to retrieve lyrics for: " + artist + " - " + title + " from " + str(LyricsOnlineSources[4]))
                else:
                    if response.status == 200:
                        text_list = self.filterTextFromOmniaLyricsIt(response.data)
                        source = "omnialyrics.it"
        windowCascade.root.title(Project_Title)
        return text_list, source

    def filterTextFromOmniaLyricsIt(self, data):
        text = BeautifulSoup(data, "html.parser")
        text = text.decode("utf-8")
        list_text = []
        # Start filtering the html content of the webpage
        if '<div class="article">' in text:  # if this is not found on the page, probably there are no lyrics yet.
            text = text.split('<div class="article">')
            text = text[1].split('</div>')
            text = text[0]
            text = text.replace("   ", "")
            text = text.replace("\n ", "\n")
            text = text.replace('<p>', "")
            text = text.replace('</p>', "")
            text = text.replace("<b>", "")
            text = text.replace("</b>", "")
            text = text.replace("<i>", "")
            text = text.replace("</i>", "")
            text = text.replace("<h2>", "")
            text = text.replace("</h2>", "")
            text = text.replace("<br>", "")
            text = text.replace("<br/>", "")
            text = text.replace("</strong>", "")
            text = text.replace("<strong>", "")
            text = text.replace("[", "")
            text = text.replace("]", "")
            if "<iframe" in text:
                text = text.split("<iframe")
                text = text[0]
            newText = ""
            for i in range(0, len(text)):
                if (text[i] >= "A" and text[i] <= "Z") or (text[i] >= "a" and text[i] <= "z") or (
                                text[i] >= "0" and text[i] <= "9"):
                    newText += text[i]
                elif text[i] == "\n":
                    if newText != "":
                        list_text.append("    " + newText)
                        newText = ""
                    if text[i - 1] == "\n" and text[i] == "\n" and text[i - 2] == "\n" and i > 3:
                        list_text.append("")
                elif i > 0:
                    if (text[i - 1] >= "A" and text[i - 1] <= "Z") or (text[i - 1] >= "a" and text[i - 1] <= "z") \
                            or text[i - 1] == "," or text[i - 1] == ".":  # this is for word spacing.
                        newText += text[i]
        return list_text

    def filterTextFromLyricsMixNet(self, data):
        text = BeautifulSoup(data, "html.parser")
        text = text.decode("utf-8")
        list_text = []
        # Start filtering the html content of the webpage
        if '<div class="entry-content">' in text:  # if this is not found on the page, probably there are no lyrics yet.
            text = text.split('<div class="entry-content">')
            text = text[1].split('<!-- lyrics_afte_post -->')
            text = text[0]
            text = text.replace("   ", "")
            text = text.replace("\n ", "\n")

            text = text.replace('<p style="text-align: center;">', "")
            text = text.replace('<p>', "")
            text = text.replace('</p>', "")
            text = text.replace("<b>", "")
            text = text.replace("</b>", "")
            text = text.replace("<i>", "")
            text = text.replace("</i>", "")
            text = text.replace("</p>", "")
            text = text.replace("<br>", "")
            text = text.replace("<br/>", "")
            text = text.replace("[", "")
            text = text.replace("]", "")
            if "<script " in text:
                text = text.split("<script ")
                text=text[0]
            if "</iframe>" in text:
                text = text.split("</iframe>")
                text = text[1]
            newText = ""
            for i in range(0, len(text)):
                if (text[i] >= "A" and text[i] <= "Z") or (text[i] >= "a" and text[i] <= "z") or (
                                text[i] >= "0" and text[i] <= "9"):
                    newText += text[i]
                elif text[i] == "\n":
                    if newText != "":
                        list_text.append("    " + newText)
                        newText = ""
                    if text[i - 1] == "\n" and text[i] == "\n" and text[i - 2] == "\n" and text[i - 3] == "\n" and i > 3:
                        list_text.append("")
                elif i > 0:
                    if (text[i - 1] >= "A" and text[i - 1] <= "Z") or (text[i - 1] >= "a" and text[i - 1] <= "z") \
                            or text[i - 1] == "," or text[i - 1] == ".":  # this is for word spacing.
                        newText += text[i]
        return list_text

    def filterTextFromGeniusCom(self, data):
        text = BeautifulSoup(data, "html.parser")
        text = text.decode("utf-8")
        list_text = []
        # Start filtering the html content of the webpage
        if '<div class="lyrics">' in text: # if this is not found on the page, probably there are no lyrics yet.
            text = text.split('<div class="lyrics">')
            text = text[1].split('</div>')
            text = text[0]
            text = text.replace("   ", "")
            text = text.replace("\n ", "\n")

            text = text.replace("<p>", "")
            text = text.replace("<b>", "")
            text = text.replace("</b>", "")
            text = text.replace("<i>", "")
            text = text.replace("</i>", "")
            text = text.replace("<!--sse-->", "")
            text = text.replace("<!--/sse-->", "")
            text = text.replace("</p>", "")
            text = text.replace("<br>", "")
            text = text.replace("<br/>", "")
            text = text.replace("[", "")
            text = text.replace("]", "")

            if "<a annotation-fragment" in text:  # if there are any adds between these lyrics, lets remove them.
                text = text.split("<a annotation-fragment=")
                aux = []
                for element in text:
                    if 'prevent-default-click="">' in element:
                        element = element.split('prevent-default-click="">')
                        aux.append(element[1])
                    else:
                        aux.append(element)
                text = "".join(aux)
                text = text.replace("</a>", "")

            newText = ""
            for i in range(0, len(text)):
                if (text[i] >= "A" and text[i] <= "Z") or (text[i] >= "a" and text[i] <= "z") or (
                        text[i] >= "0" and text[i] <= "9"):
                    newText += text[i]
                elif text[i] == "\n":
                    if newText != "":
                        list_text.append("    " + newText)
                        newText = ""
                    if text[i - 1] == "\n" and text[i] == "\n" and text[i - 2] == "\n" and i > 3:
                        list_text.append("")
                elif i > 0:
                    if (text[i - 1] >= "A" and text[i - 1] <= "Z") or (text[i - 1] >= "a" and text[i - 1] <= "z") \
                            or text[i - 1] == "," or text[i - 1] == ".":  # this is for word spacing.
                        newText += text[i]
        return list_text

    def filterTextFromLyricsMy(self, data):
        text = BeautifulSoup(data, "html.parser")
        text = text.decode("utf-8")
        list_text = []
        # Start filtering the html content of the webpage
        if '<div class="show_lyric">' in text: # if this is not found on page, it means there are no lyrics
            text = text.split('<div class="show_lyric">')
            text = text[1].split('</div>')
            text = text[0]
            text = text.replace("   ", "")
            text = text.replace("\n ", "\n")

            text = text.replace("<p>", "")
            text = text.replace("<b>", "")
            text = text.replace("</b>", "")
            text = text.replace("<i>", "")
            text = text.replace("</i>", "")
            text = text.replace("</p>", "")
            text = text.replace("<br>", "")
            text = text.replace("</br>", "")
            text = text.replace("<br/>", "")
            text = text.replace("[", "(")
            text = text.replace("]", ")")
            newText = ""
            for i in range(0, len(text)):
                if (text[i] >= "A" and text[i] <= "Z") or (text[i] >= "a" and text[i] <= "z") or (
                        text[i] >= "0" and text[i] <= "9") or text[i] == "(" or text[i] == ")":
                    newText += text[i]
                elif text[i] == "\n":
                    if newText != "":
                        list_text.append("    " + newText)
                        newText = ""
                    if newText =="" and len(list_text)>1 and list_text[(len(list_text)-1)]!="" and list_text[(len(list_text)-2)]!="":
                        list_text.append("")
                elif i > 0:
                    if (text[i - 1] >= "A" and text[i - 1] <= "Z") or (text[i - 1] >= "a" and text[i - 1] <= "z") \
                            or text[i - 1] == "," or text[i - 1] == "." or text[i - 1] == "?" or text[i - 1] == "!":  # this is for word spacing.
                        newText += text[i]
        return list_text

    def LyricsDisplay(self): #to be continued
        text_list, source = self.accessPage()
        if len(text_list) > 0:
            self.Lyrics.set("Lyrics for '" + play_list.validFiles[self.songIndex].Artist + " - " \
                            + play_list.validFiles[self.songIndex].Title + "' -> were found on " + source + ":")
            for element in text_list:
                self.listboxLyrics.insert(tk.END, element)
                if len(element) > 55 and len(element) > self.listboxLyrics["width"]:  # this will resize the window and the listbox to fit the lyrics.
                    listboxX = len(element) - 55
                    windowX = 580 + (listboxX * 10)  # 580 is the initial value of the window
                    listboxX += 65  # 65 is the initial width of the listbox
                    self.top.geometry(str(windowX) + "x550+100+100")
                    self.listboxLyrics["width"] = listboxX
            self.SaveLyrics.config(state=tk.NORMAL)
        else:
            self.Lyrics.set("Lyrics for '" + play_list.validFiles[self.songIndex].Artist + " - " \
                            + play_list.validFiles[self.songIndex].Title + "' -> were NOT found!\n" +
                            "Make sure you have 'Artist' and 'Title' Tags filled properly.")

    def copy_to_clipboard(self, event, value):
        self.top.clipboard_clear()
        self.top.clipboard_append(value)

    def rightClickOnLyrics(self, event):
        listboxSelectedEvent = event.widget
        if len(listboxSelectedEvent.curselection()) > 0:
            index = int(listboxSelectedEvent.curselection()[0])
            value = self.listboxLyrics.get(index)
            aMenu = tk.Menu(windowCascade.root, tearoff=0)
            aMenu.add_command(label='Copy All', command= lambda: self.copy_to_clipboard("<ButtonPress-3>", "\n".join(self.listboxLyrics.get(0, tk.END))))
            if value!="":
                aMenu.add_command(label='Copy Line', command= lambda: self.copy_to_clipboard("<ButtonPress-3>", value))
            aMenu.post(event.x_root, event.y_root)

#class defined to describe the behavior of a web-crawler set up to look for information about a given artist
class GrabArtistBio(Window):
    def __init__(self, index="empty"):
        global allButtonsFont
        self.LyricsDownloads = rootDirectory + "/LyricsDownloads.lyl"
        if index == "empty":
            index = play_list.currentSongIndex  # do not forget that currentSongIndex can be None
        self.songIndex = index
        if self.songIndex != None:  # make sure there is a song to search lyrics for.
            windowCascade.GrabArtistBio = self
            color = PauseButton["bg"]  # get the color which the rest of elements is using at the moment
            self.top = tk.Toplevel(windowCascade.root, bg=color)
            Window_Title = "Artist Bio"
            self.top.title(Window_Title)
            self.top.geometry("490x350+" + str(windowCascade.root.winfo_x()+100) + "+" + str(windowCascade.root.winfo_y()+100))
            self.top.protocol("WM_DELETE_WINDOW", self.destroy)
            self.top.attributes('-alpha', play_list.windowOpacity)

            self.Message = StringVar()
            self.Message.set("According to LastFM:\n\n")
            tk.Label(self.top, textvariable=self.Message, fg=fontColor.get(), font=allButtonsFont.get(),
                     bg=color).place(x=5, y=5)
            self.BioText = StringVar()
            self.BioText.set("Artist Bio:")
            tk.Label(self.top, textvariable=self.BioText, fg=fontColor.get(), font=allButtonsFont.get(), bg=color).place(x=15, y=45)
            self.frame = tk.Frame(self.top, width=100, height=30, bg=color, borderwidth=1)
            self.frame.place(x=5, y=65)
            self.scrlbar = ttk.Scrollbar(self.frame, orient="vertical")
            self.listboxLyrics = tk.Listbox(self.frame, fg=fontColor.get(), font=allButtonsFont.get(), width=55, bg=color, height=15, relief=tk.GROOVE, \
                                    yscrollcommand=self.scrlbar.set, borderwidth=2, selectbackground = fontColor.get(), selectforeground = color)
            self.listboxLyrics.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.X)
            self.listboxLyrics.bind('<ButtonPress-3>', self.rightClickOnLyrics)
            self.scrlbar.config(command=self.listboxLyrics.yview)
            self.scrlbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.ArtistBioDisplay()
            self.top.bind("<Tab>", self.focus_out)
            self.top.bind("<Escape>", self.destroyEsc)

            #Preparing parties for resizing window to fit content
            self.frame["width"] = self.listboxLyrics.winfo_reqwidth() + self.scrlbar.winfo_reqwidth()
            self.frame["height"] = self.listboxLyrics.winfo_reqheight() + self.scrlbar.winfo_reqheight()
            calculateResizeWindow(self.top, [self.frame], 30)
        else:
            WindowDialog("Playlist is empty.", Button1_Functionality=ButtonFunctionality("OK", None),
                         windowTitle="Artist Bio")

    def accessPage(self):
        urllib3.disable_warnings()
        text_list = []
        if play_list.validFiles[self.songIndex].Artist != "Various":
            artist = play_list.validFiles[self.songIndex].Artist
            artist = artist.replace("'", "")
            artist = artist.replace(",", "")
            artist = artist.replace(":", "")
            artist = artist.replace(".", "")
            artist = artist.replace("!", "")
            artist = artist.replace("%", "")
            artist = artist.replace("?", "")
            artist = artist.replace("`", "")
            artist = artist.replace("`", "")
            artist = artist.replace(" & ", " and ")
            artist = artist.replace("&", " and ")
            artist = artist.replace(".mp3", "")
            artist = artist.replace(".MP3", "")
            artist = artist.replace(".mP3", "")
            artist = artist.replace(".Mp3", "")
            artist = artist.replace(" ", "+")
            url = "https://www.last.fm/music/" + artist + "/+wiki" # this is possible to change with time. Let's hope it doesn't
            http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=2.0, read=2.0), retries=2)
            try:
                response = http.request('GET', url)
            except NewConnectionError as exp:  # This is the correct syntax
                text = ("Unable to establish connection to the server: last.fm" +
                        "\nError Message: " + str(exp) +
                        "\nPlease check your internet connection before proceed.")
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
            except Exception:
                text = ("An exception has been handled. \nI am sorry but I'm unable to retrieve info.")
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
            else:
                if response.status == 200:
                    text_list = self.filterTextFromLastFM(response.data)
        return text_list

    def filterTextFromLastFM(self, data):
        text = BeautifulSoup(data, "html.parser")
        text = text.decode("utf-8")
        list_text = []
        # Start filtering the html content of the webpage
        if '<div class="wiki-content" itemprop="description">' in text: # if condition not fulfilled it means the artist is on lastFM but nothing was written about him.
            text = text.split('<div class="wiki-content" itemprop="description">')
            text = text[1].split('</div>')
            text = text[0]
            text = text.replace("   ", "")

            text = text.replace("<a>", "")
            text = text.replace("</a>", "")
            text = text.replace("<b>", "")
            text = text.replace("</b>", "")
            text = text.replace("<p>", "")
            text = text.replace("</p>", "")
            text = text.replace("<strong>", "")
            text = text.replace("</strong>", "")
            text = text.replace("</br>", "")
            text = text.replace("<br/>", "")
            text = text.replace("<br>", "")
            text = text.replace("<em>", "")
            text = text.replace("</em>", "")
            text = text.replace("<i>", "")
            text = text.replace("</i>", "")
            if "<a " in text:  # if there are any adds between these lyrics, lets remove them.
                text = text.split("<a ")
                aux = []
                for element in text:
                    if '">' in element:
                        element = element.split('">')
                        aux.append(element[1] + " ")
                    else:
                        aux.append(element)
                text = "".join(aux)
                text = text.replace("</a>", "")
            if "<sup " in text:  # if there are any adds between these lyrics, lets remove them.
                text = text.split("<sup ")
                aux = []
                for element in text:
                    if '</sup>' in element:
                        element = element.split('</sup>')
                        aux.append(element[1])
                    else:
                        aux.append(element)
                text = "".join(aux)
                text = text.replace("</a>", "")
            newText = ""
            splitParagraph = False
            for i in range(0, len(text)):
                if text[i] != "\n":
                    newText += text[i]
                if (text[i] == "." and i < len(text)-1 and text[i+1]==" ") and (len(list_text)%5==0 or splitParagraph): #make a new paragraph after each 5 sentences.
                    list_text.append("  " + newText)
                    newText = ""
                    list_text.append("") #add an empty line
                elif len(newText)>=45 and (text[i]==" " or text[i] =="-"):
                    list_text.append("  " +newText)
                    newText=""
                if len(list_text) % 5 > 0 and len(list_text) % 5 < 3 and len(list_text) > 5:
                    splitParagraph = True
            if newText!="":
                list_text.append("  " +newText)
                newText=""
        return list_text

    def ArtistBioDisplay(self): #to be continued
        text_list = self.accessPage()
        if len(text_list) > 0:
            for element in text_list:
                self.listboxLyrics.insert(tk.END, element)
        else:
            self.listboxLyrics.insert(tk.END, "No information found")

    def copy_to_clipboard(self, event, value):
        self.top.clipboard_clear()
        self.top.clipboard_append(value)

    def rightClickOnLyrics(self, event):
        listboxSelectedEvent = event.widget
        if len(listboxSelectedEvent.curselection()) > 0:
            index = int(listboxSelectedEvent.curselection()[0])
            value = self.listboxLyrics.get(index)
            aMenu = tk.Menu(windowCascade.root, tearoff=0)
            aMenu.add_command(label='Copy All', command= lambda: self.copy_to_clipboard("<ButtonPress-3>", "\n".join(self.listboxLyrics.get(0, tk.END))))
            if value!="":
                aMenu.add_command(label='Copy Line', command= lambda: self.copy_to_clipboard("<ButtonPress-3>", value))
            aMenu.post(event.x_root, event.y_root)

#class defined to describe the behavior of a tooltip message on hovering over an element
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        def enter(event):
            self.showTooltip()

        def leave(event):
            self.hideTooltip()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def showTooltip(self):
        self.tooltipwindow = tk.Toplevel(self.widget)
        #Configuring window without border and no normal means of closing
        self.tooltipwindow .wm_overrideredirect(1)

        self.tooltipwindow .wm_geometry("+{}+{}".format(self.widget.winfo_rootx(), self.widget.winfo_rooty() + 30))

        label = tk.Label(self.tooltipwindow, text=self.text, background="#ffffe0", relief='solid',
                         borderwidth=1, fg="black", anchor="e", justify=tk.LEFT,
                         wraplength=self.widget.winfo_reqwidth()-4)
        label.pack()

    def hideTooltip(self):
        if self.tooltipwindow != None:
            self.tooltipwindow.destroy()
            self.tooltipwindow = None

#class defined to store references for menubar menus
class MenuBar:
    def __init__(self):
        self.root = None
        self.selectedToken = "-> "

#class defined to store references for app opened windowses
class playerWindowCascade:
    def __init__(self):
        self.root = None
        self.Customize = None
        self.WindowDialog = []
        self.Mp3TagModifierTool = None
        self.SleepingTool = None
        self.Slideshow = None
        self.CuttingTool = None
        self.GrabLyricsTool = None
        self.GrabArtistBio = None

    def reinitializeOpenedWindows(self):
        if self.root != None:
            if self.Customize != None:
                self.Customize.destroy()
                Customize(self.root)
            if len(self.WindowDialog) > 0:
                for index in range(0, len(self.WindowDialog)):
                    #We will always operate on index 0 as when we call the destroyer element
                    #gets removed, then when we recreate the WindowDialog again the element gets added at the end
                    text = self.WindowDialog[0].textValue
                    button1_func = self.WindowDialog[0].Button1_Func
                    button2_func = self.WindowDialog[0].Button2_Func
                    title = self.WindowDialog[0].windowTitle
                    self.WindowDialog[0].destroy()
                    WindowDialog(text, button1_func, button2_func, title)
            if self.Mp3TagModifierTool != None:
                self.Mp3TagModifierTool.destroy()
                Mp3TagModifierTool()
            if self.SleepingTool != None:
                self.SleepingTool.destroy()
                SleepingTool(self.root)
            if self.Slideshow != None:
                self.Slideshow.destroy()
                Slideshow()
            if self.CuttingTool != None:
                self.CuttingTool.destroy()
                CuttingTool(self.root)
            if self.GrabLyricsTool != None:
                index = self.GrabLyricsTool.songIndex # store the index of the song for which the lyrics are shown
                self.GrabLyricsTool.destroy()
                GrabLyricsTool(index)
            if self.GrabArtistBio != None:
                index = self.GrabArtistBio.songIndex # store the index of the song for which the lyrics are shown
                self.GrabArtistBio.destroy()
                GrabArtistBio(index)

#A class defined to store multiple values in same datq unit for hotkey triggers
class hotkeyTriggers:
    def __init__(self):
        self.nextSongTrigger = False
        self.previousSongTrigger = False
        self.playPauseTrigger = False

#A class defined to store multiple skin/theme appearance settings
class Skin():
    def __init__(self, button_bg, font, background_image, font_color="white",
                 label_bg_color="lightgray", unique_font_color = False, skin_name = ""):
        self.background_color = button_bg
        self.button_font_color = font_color
        self.label_font_color = font_color
        self.unique_font_color = unique_font_color
        if unique_font_color == False:
            label_font_color = button_bg
        self.label_bg_color = label_bg_color
        self.font = font
        self.background_image = background_image
        self.skin_name = skin_name
        if skin_name =="":
            self.skin_name = self.background_color

    def getLabelTextColor(self):
        if self.unique_font_color:
            return self.button_font_color
        else:
            return self.background_color

    def changingSkin(self):  # this function is called when new skin is selected from the menubar
        global SkinColor
        global allButtonsFont
        global labelBackground
        global play_list
        global labelTextColor
        global backgroundFile

        if self.background_color == "custom":
            showCustomizeWindow()
        else:
            fontColor.set(self.button_font_color)  # default value
            backgroundFile = self.background_image
            labelBackground.set(self.label_bg_color)
            labelTextColor = self.label_font_color
            allButtonsFont.set(self.font)
            SkinColor.set(self.background_color)
            play_list.skin_theme = self
            changeSkin("<Double-Button>")

    def __eq__(self, other):
        if (self.background_color == other.background_color and self.button_font_color == other.button_font_color \
                        and self.label_font_color == other.label_font_color and
                        self.unique_font_color == other.unique_font_color and \
                        self.font == other.font and self.background_image == other.background_image) \
                        and self.label_bg_color == other.label_bg_color:
            return True
        else:
            return False

#A class to define a customize scheduler
class Scheduler(sched.scheduler):
    def __init__(self, delay:float, priority: int, function:callable,  timefunc=time.monotonic, delayfunc=time.sleep):
        super().__init__(timefunc, delayfunc)
        self.isMainLoopSuspended = False #this variable will be used to signal the disabling of scheduling
        self.userIntervention = False # this variable will be used to identify whether the user affected the play_list
        self.time_stamp = None
        self.function = function
        self.delay = delay
        self.priority = priority

    def enter_mainloop(self):
        #this method will call recurrently the function self was initialzied with
        #this method is supposed to be used outside indeterminate loops in order to maintain the GUI responsive
        if APPLICATION_EXIT == False:
            if self.isMainLoopSuspended == False:
                try:
                    super().enter(self.delay, self.priority, self.enter_mainloop)
                    self.function()
                except Exception as exp:
                    text = ("Enter Scheduler: \n" + str(exp))
                    WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle="Warning")
        else:
            # Window was close - Application should be destroyed and Progress should be saved
            # Make a backup of everything:
            file = open(automaticallyBackupFile, "wb")
            pickle.dump(play_list, file)
            file.close()
            sys.exit()

    def suspend_mainloop(self):
        #this method will suspend the recurent calling of self.function
        self.isMainLoopSuspended = True

    def resume_mainloop(self):
        #this method will resume the recurrent calling of self.function
        if self.isMainLoopSuspended == True:
            self.isMainLoopSuspended = False
            self.enter_mainloop()

    def single_loop(self):
        #this method will call the self.function when the delay expires
        #this method is supposed to be used within loops to provide responsiveness
        if self.isMainLoopSuspended == True:
            if self.time_stamp == None:
                self.time_stamp = time.time()
            if time.time() - self.time_stamp >= self.delay:
                self.function()


def formatSlashesInFilePath(filepath):
    #this will turn every type of slashes into '/'
    if "\\\\" in filepath:
        # enter here if filepath is formated with \\ slashes
        filepath = filepath.replace("\\\\", "/")
    if "\\" in filepath:
        # enter here if the filepath is formated with \ slash
        filepath = filepath.replace("\\", "/")
    elif "//" in filepath:
        # enter here if filepath is formated with // slashes
        filepath = filepath.replace("//", "/")

    return filepath

def getFileNameFromFilePath(filepath):
    #this function will get the name of a file from the filepath
    #should work also with directories if they don't end with slash
    filename = ""

    filepath = formatSlashesInFilePath(filepath)

    filename = re.split("/", filepath)
    filename = filename[len(filename) - 1]
    return filename

#menubar variable to store references to the separate menus added to the menubar
menubar = MenuBar()

#windowCascade variable to store references to the App opened windowses
windowCascade = playerWindowCascade()

#monitor of keyboard hotkeys
hotkeyMonitor = hotkeyTriggers()

scriptFileName = getFileNameFromFilePath(sys.argv[0])
rootDirectory = str(sys.argv[0]).replace(scriptFileName, "")

if rootDirectory.endswith("/") == True:
    rootDirectory = rootDirectory[0:len(rootDirectory)-1]

playerIcon = rootDirectory + "/resources/headphone_red.ico"

clearPlaybackFile = rootDirectory + "/resources/clear.mp3"
SongStatsFileName = rootDirectory + "/backup/SongStats.sts"
automaticallyBackupFile = rootDirectory + "/backup/PlayListBackup.pypl"

allButtonsWidth = 11
allButtonsHeight = 1

#list of possible online sources for finding song lyrics
LyricsOnlineSources = ["all", "genius.com", "lyrics.my", "lyricsmix.net", "omnialyrics.it"]

#list of custom colors available for selection in the Customize window
custom_color_list = ["green", "yellow", "purple", "black", "brown", "sienna", "cyan", "magenta", "royalblue1",
                      "midnight blue",
                     "pink", "blue", "darkblue", "darkgreen", "deeppink", "red", "red2", "red3", "red4", "red3", \
                     "orange", "gold", "silver", "indigo", "lightgray", "white", "gray", "indian red", "darkorchid4",
                     "darkorchid3", "darkorchid2", "darkorchid1", "limegreen"]

custom_color_list = sorted(custom_color_list)

#list of custom fonts available for selection in Customize Window
custom_font_list = ["Arial 9", "Arial 10", "Arial 9 bold", "Arial 10 bold",
                    "Consolas 9", "Consolas 9 bold", "Consolas 10", "Consolas 10 bold", "Consolas 11", "Consolas 11 bold",
                    "Courier 9", "Courier 10", "Courier 11", "Courier 9 bold", "Courier 10 bold", "Courier 11 bold",
                    "Century 9", "Century 10", "Century 9 bold", "Century 10 bold",
                    "Verdana 9", "Verdana 10", "Verdana 9 bold", "Verdana 10 bold",
                    "Georgia 9", "Georgia 10", "Georgia 9 bold", "Georgia 10 bold",
                    "Garamond 9", "Garamond 10", "Garamond 11", "Garamond 9 bold", "Garamond 10 bold","Garamond 11 bold",
                    "Tahoma 9", "Tahoma 10", "Tahoma 11", "Tahoma 9 bold", "Tahoma 10 bold", "Tahoma 11 bold",
                    "Rockwell 9", "Rockwell 10", "Rockwell 11", "Rockwell 9 bold", "Rockwell 10 bold", "Rockwell 11 bold",
                    "Fixedsys 9","Fixedsys 10",
                    "Candara 9", "Candara 10", "Candara 9 bold", "Candara 10 bold",
                    "Impact 9", "Impact 10", "Impact 11",
                    "Calibri 9", "Calibri 10", "Calibri 9 bold", "Calibri 10 bold",
                    "Modern 9", "Modern 10", "Modern 11", "Modern 9 bold", "Modern 10 bold", "Modern 11 bold",
                    "Harrington 9", "Harrington 10", "Harrington 11", "Harrington 9 bold", "Harrington 10 bold", "Harrington 11 bold",
                    "Stencil 9", "Stencil 10", "Stencil 11",
                    "Forte 9", "Forte 10", "Forte 11",
                    "System 9",
                    "SimSun 9","SimSun 10", "SimSun 11", "SimSun 12", "SimSun 9 bold","SimSun 10 bold", "SimSun 11 bold", "SimSun 12 bold",
                    "Terminal 9", "Terminal 10", "Terminal 11",
                    "Times 9", "Times 10", "Times 11", "Times 9 bold", "Times 10 bold", "Times 11 bold",
                    "Unispace 9", "Unispace 10", "Unispace 11",
                    "Haettenschweiler 9", "Haettenschweiler 10", "Haettenschweiler 11",
                    "Perpetua 9", "Perpetua 10", "Perpetua 11", "Perpetua 9 bold", "Perpetua 10 bold", "Perpetua 11 bold",
                    "Perpetua 12", "Perpetua 12 bold"]

custom_font_list = sorted(custom_font_list)

radioButtonsDefaultColor = "lightgray" #background color for radiobuttons used for Song Rating

progressViewRealTime = 0.1 #value in seconds, used to schedule the scheduler

listBox_Song_selected_index = None #the active index for the listbox
APPLICATION_EXIT = False #flag to tell us whether the user Closed the Main Window or not

skinOptions = []
skinOptions.append(Skin(skin_name = "Light Blue", button_bg = "blue", font="Consolas 10 bold", background_image=rootDirectory + "/resources/default.gif", font_color="white"))
skinOptions.append(Skin(skin_name = "Light Red", button_bg = "red", font="Rockwell 10 bold", background_image=rootDirectory + "/resources/minilights.gif", font_color="white"))
skinOptions.append(Skin(skin_name = "Light Gray", button_bg = "gray", font="Arial 10 italic", background_image=rootDirectory + "/resources/road.gif", font_color="white"))
skinOptions.append(Skin(skin_name = "Light Green", button_bg = "green", font="Candara 10 bold", background_image=rootDirectory + "/resources/darkg.gif", font_color="white"))
skinOptions.append(Skin(skin_name = "Light Deeppink", button_bg = "deeppink", font="Arial 10 bold", background_image=rootDirectory + "/resources/leaves.gif", font_color="white"))
skinOptions.append(Skin(skin_name = "Light Darkblue", button_bg = "darkblue", font="Calibri 10 bold", background_image=rootDirectory + "/resources/darkblue.gif", font_color="white"))
skinOptions.append(Skin(skin_name = "Light Sienna", button_bg = "sienna", font="Harrington 10 bold", background_image=rootDirectory + "/resources/map.gif", font_color="white"))
skinOptions.append(Skin(skin_name = "Light Indigo", button_bg = "indigo", font="Fixedsys 11", background_image=rootDirectory + "/resources/space.gif", font_color="white"))
skinOptions.append(Skin(skin_name = "Light Black", button_bg = "black", font="Stencil 10", background_image=rootDirectory + "/resources/universe.gif", font_color="white"))
skinOptions.append(Skin(skin_name = "Modern Red", button_bg = "black", font="Tahoma 9", background_image=rootDirectory + "/resources/minilights.gif", font_color="red", unique_font_color=True, label_bg_color="black"))
skinOptions.append(Skin(skin_name = "Modern White", button_bg = "white", font="Rockwell 10", background_image=rootDirectory + "/resources/silver.gif", font_color="black", unique_font_color=True, label_bg_color="white"))
skinOptions.append(Skin(skin_name = "Modern Brown", button_bg = "brown", font="Verdana 9", background_image=rootDirectory + "/resources/leaves.gif", font_color="black", unique_font_color=False, label_bg_color="black"))
skinOptions.append(Skin(skin_name = "Modern Purple", button_bg = "purple", font="Verdana 9", background_image=rootDirectory + "/resources/universe.gif", font_color="cyan", unique_font_color=True, label_bg_color="black"))
skinOptions.append(Skin(skin_name = "Dark Black", button_bg = "black", font="Perpetua 11 bold", background_image=rootDirectory + "/resources/space.gif", font_color="pink", unique_font_color=True, label_bg_color="black"))
skinOptions.append(Skin(skin_name = "Retro Red", button_bg = "red3", font="Terminal 11", background_image=rootDirectory + "/resources/retro_red.gif", font_color="black", unique_font_color=True, label_bg_color="red3"))
skinOptions.append(Skin(skin_name = "Red Blue", button_bg = "blue2", font="Impact 10", background_image=rootDirectory + "/resources/red_blue.gif", font_color="red", unique_font_color=True, label_bg_color="blue2"))
skinOptions.append(Skin(skin_name = "Blue Lights", button_bg = "black", font="Modern 10", background_image=rootDirectory + "/resources/blue_lights.gif", font_color="cyan", unique_font_color=True, label_bg_color="black"))
skinOptions.append(Skin(skin_name = "Purple Neon", button_bg = "darkorchid4", font="Calibri 10 bold", background_image=rootDirectory + "/resources/purple_neon.gif", font_color="lightgray", unique_font_color=True, label_bg_color="darkorchid4"))
skinOptions.append(Skin(skin_name = "Dark Cyan", button_bg = "gray14", font="Rockwell 9 bold", background_image=rootDirectory + "/resources/dark_cyan.gif", font_color="cyan", unique_font_color=True, label_bg_color="gray14"))
skinOptions.append(Skin(skin_name = "Midnight Blue", button_bg = "midnight blue", font="Courier 9 bold", background_image=rootDirectory + "/resources/midnight_blue.gif", font_color="silver", unique_font_color=True, label_bg_color="midnight blue"))
skinOptions.append(Skin(skin_name = "Royal Blue", button_bg = "gray12", font="Arial 10 bold", background_image=rootDirectory + "/resources/royal_blue.gif", font_color="royalblue1", unique_font_color=True, label_bg_color="gray12"))
skinOptions.append(Skin(skin_name = "Black Green", button_bg = "gray10", font="Garamond 11 bold", background_image=rootDirectory + "/resources/black_green.gif", font_color="limegreen", unique_font_color=True, label_bg_color="gray10"))
skinOptions.append(Skin(skin_name = "Black Red", button_bg = "gray8", font="SimSun 12 bold", background_image=rootDirectory + "/resources/black_red.gif", font_color="red2", unique_font_color=True, label_bg_color="gray8"))
skinOptions.append(Skin(button_bg = "custom", font="", background_image="", font_color=""))

play_list = Playlist() #playlist

progressBarMargin = 10

visualSongNameLabel = None

s_rate = None # will store the sample_rate for the song loaded in the playback
channels = None # will store the number of channels (Mono / Stereo) for the song loaded in the playback
temp_SongEndPos = None #this variable will only be used when CrossFade is enabled.

FLAGGED_MAXIMUM_ITERATIONS = 10 #threshold for invalid files looped consecutively
flagged_files_looped_consecutively = 0 #variable to track how many invalid/flagged files get looped consecutively
#will use it to stop the scheduling loop if a threshold is reached.

timeListenedProgress = 0 #variable to help calculate the time spent listening to song / playlist

def calculateListenedTimeSinceLastIter(song_position):
    #function to help calculate the time spent listening to song / playlist
    global timeListenedProgress
    value = song_position - timeListenedProgress
    timeListenedProgress = song_position
    return value

def load_file(fileToPlay=None):
    #this function is called when clicking on Open File command in Menubar File Menu.
    #this function will validate the .mp3 file from user's selection.
    #if the files are valid they will be appended to the playlist
    global play_list
    global listBox_Song_selected_index
    #Open the file dialog only if the function is called without a parameter
    if type(play_list.dirFilePath) == str:
        #if using the old version of playlist - convert the data type for this variable
        play_list.dirFilePath = list(play_list.dirFilePath)
    if fileToPlay==None:
        dir = play_list.dirFilePath[len(play_list.dirFilePath)-1] if len(play_list.dirFilePath) > 0 else "/"
        fileToPlay = filedialog.askopenfilenames(initialdir = dir, title = "Select file",filetypes = (("mp3 files","*.mp3"),("pypl files","*.pypl"),("all files","*.*")))
    if fileToPlay:
        fileToPlay = list(fileToPlay)
        directory_path = fileToPlay[0].replace(getFileNameFromFilePath(fileToPlay[0]), "")
        if directory_path.endswith("/"):
            #if it ends with forward slash we will remove the forward slash.
            #the filedialog.askdirectory does not end with forward slash, we will need to check if Locations are identical
            #so we don't store them twice or loop through same dirs multiple times.
            directory_path = directory_path[0: len(directory_path)-1]

        play_list.dirFilePath.append(directory_path)
        play_list.dirFilePath = list(set(play_list.dirFilePath)) #don't store duplicates
        dict_list = []
        if play_list.keepSongsStats and os.path.isfile(SongStatsFileName):
            try:
                file = open(SongStatsFileName, "rb")
                dict_list = pickle.load(file)
                file.close()
            except:
                text = ("Could not load the songs stats. File might be corrupted.")
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
        i=0
        messageForUser = ""
        scheduler.suspend_mainloop()  # we will keep window refreshed in the loop
        for file in fileToPlay:
            if file.lower().endswith(".mp3"):
                i+=1
                if scheduler.userIntervention == True:
                    # user changed something in the play_list that might affect the outcome of this loop
                    scheduler.userIntervention = False
                    break
                windowCascade.root.title("Scanning: " + str(i) + " out of " + str(len(fileToPlay)) + " files")
                scheduler.single_loop() # this will make the main window responsive
                song = Song(file)
                if song.Exception == None and song not in play_list.validFiles:
                    if play_list.keepSongsStats and dict_list != []:
                        loadSongStats(song, dict_list)
                    play_list.validFiles.append(song)
                    listbox.insert(len(play_list.validFiles)-1,
                                   str(len(play_list.validFiles)-1) + ". " + song.fileName)
                    if len(play_list.validFiles) == 1:
                        #do this only when the first element is added
                        play_list.currentSongIndex = 0
                        listBox_Song_selected_index = 0
                        SongName.set("Paused: " + play_list.validFiles[play_list.currentSongIndex].fileName)
                    textFilesToPlay.set("Files: " + str(len(play_list.validFiles)))
                    play_list.playTime += song.Length
                elif song in play_list.validFiles:
                    messageForUser += str(song.filePath) + "\n" + "File already exists in the playlist at index: " \
                                        + str(play_list.validFiles.index(song)) + "\n\n"
                else:
                    messageForUser += str(song.filePath) + "\n" + "Reason: " + str(song.Exception) + "\n\n"

            elif ".pypl" in file:
                loadPlaylistFile(file)
                configurePlayer()

        scheduler.resume_mainloop()

        if messageForUser != "":
            text = "Unable to load the following MP3 Files: \n\n" + messageForUser
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None),
                                        windowTitle="Information")

        windowCascade.root.title(Project_Title)
        #displayElementsOnPlaylist() #not neeed the listbox was populated above
        showCurrentSongInList()
        play_list.isListOrdered = 21 #this will mean Custom Sorting
        updateSortMenuLabel()

def loadPlaylistFile(fileURL):
    #this function is called at startup if there is a backup Playlist file -> automaticallyBackupFile.
    #also this function is used if the user opens a .pypl file
    global play_list
    try:
        file = open(fileURL, "rb")
        content = pickle.load(file)
        file.close()
    except Exception as exp:
        text = ("Load Playlist File Exception: " + str(exp) +
                "\n\nFile: " + str(fileURL) + " might be corrupted.")
        tk.messagebox.showinfo("Warning", text)
    else:
        if isinstance(content, Playlist):
            existingFiles = play_list.validFiles
            play_list = content
            play_list.validFiles = existingFiles + play_list.validFiles

            #if using old version of playlist file - update it with missing fields
            if hasattr(play_list, "playerWidth") == False:
                setattr(play_list, "playerWidth", 300)
            if hasattr(play_list, "playerHeight") == False:
                setattr(play_list, "playerHeight", 510)
            if hasattr(play_list, "skin_theme") == False:
                background_color = skinOptions[play_list.skin].background_color
                font = skinOptions[play_list.skin].font

                bg_picture = skinOptions[play_list.skin].background_image.replace(rootDirectory + "/", "")
                label_background_color = skinOptions[play_list.skin].label_bg_color
                font_color = skinOptions[play_list.skin].button_font_color
                unique_colors = skinOptions[play_list.skin].unique_font_color

                if play_list.customElementBackground != None :
                    background_color = custom_color_list[play_list.customElementBackground]
                if play_list.customFont != None:
                    font = custom_font_list[play_list.customFont]
                if play_list.customBackgroundPicture != None:
                    bg_picture = play_list.customBackgroundPicture.replace("./", "")
                if play_list.customLabelBackground != None:
                    label_background_color = custom_color_list[play_list.customLabelBackground]
                if play_list.customFontColor != None:
                    font_color = custom_color_list[play_list.customFontColor]
                if play_list.customChangeBackgroundedLabelsColor != None:
                    unique_colors = play_list.customChangeBackgroundedLabelsColor

                setattr(play_list, "skin_theme",
                        Skin(button_bg = background_color,
                             font = font,
                             background_image = bg_picture,
                             font_color = font_color,
                             label_bg_color = label_background_color,
                             unique_font_color = unique_colors,
                             skin_name = ""))
                del play_list.customFont
                del play_list.customElementBackground
                del play_list.customLabelBackground
                del play_list.customBackgroundPicture
                del play_list.customFontColor
                del play_list.customChangeBackgroundedLabelsColor
                del play_list.skin
            del content
        else:
            text = ("Playlist file has been corrupted.")
            tk.messagebox.showinfo("Warning", text)

def configurePlayer():
    #this function is called at startup to configure the player Main Window elements
    global play_list

    if play_list.currentSongIndex != None and len(play_list.validFiles) > 0:
        #in case the user uses older version of playlist
        if hasattr(play_list.validFiles[play_list.currentSongIndex], "Exception") == False:
            #add the missing attribute
            setattr(play_list.validFiles[play_list.currentSongIndex], "Exception", None)
        if(play_list.validFiles[play_list.currentSongIndex].Exception == None):
            SongName.set("Paused: " + play_list.validFiles[play_list.currentSongIndex].fileName)
        else:
            SongName.set("Flagged: " + play_list.validFiles[play_list.currentSongIndex].fileName)
        SongSize.set("Size: " + str(play_list.validFiles[play_list.currentSongIndex].fileSize) + " MB")
        if play_list.progressTime == "Ascending":
            textProgress.set(
                "Time Elapsed: " + formatTimeString(play_list.currentSongPosition))
        else:
            SongLength = int(play_list.validFiles[play_list.currentSongIndex].Length - play_list.currentSongPosition)
            textProgress.set("Time Left: " + formatTimeString(SongLength))
        # Update Length
        songLength = float(
            "{0:.0f}".format(play_list.validFiles[play_list.currentSongIndex].Length))  # no decimals needed
        textLength.set("Length: "+ formatTimeString(songLength))
        textGenre.set("Genre: " + str(play_list.validFiles[play_list.currentSongIndex].Genre))
        textArtist.set("Artist: " + str(play_list.validFiles[play_list.currentSongIndex].Artist))
        textAlbum.set("Album: " + str(play_list.validFiles[play_list.currentSongIndex].Album))
        textTitle.set("Title: " + str(play_list.validFiles[play_list.currentSongIndex].Title))
        textYear.set("Year: " + str(play_list.validFiles[play_list.currentSongIndex].Year))
        textSongListenedTime.set("Played time: "+ formatTimeString(int(play_list.validFiles[play_list.currentSongIndex].SongListenedTime)))
        textPlaylistListenedTime.set(
            "Total listening time: " + formatTimeString(int(play_list.PlaylistListenedTime)))
        startPos = int(play_list.validFiles[play_list.currentSongIndex].startPos)
        textStartTime.set("Starts at: "+ formatTimeString(startPos))
        endPos = int(play_list.validFiles[play_list.currentSongIndex].endPos)
        textEndTime.set("Ends at: "+ formatTimeString(endPos))
        textFadeIn.set("FadeIn: " + str(play_list.validFiles[play_list.currentSongIndex].fadein_duration) + "s")
        textFadeOut.set("FadeOut: " + str(play_list.validFiles[play_list.currentSongIndex].fadeout_duration) + "s")
        mode = "Stereo" if play_list.validFiles[play_list.currentSongIndex].channels == 2 else "Mono"
        textMonoStereoMode.set("Mode: " + mode)
        textNofPlays.set("No. of Plays: " + str(play_list.validFiles[play_list.currentSongIndex].NumberOfPlays))
        textSampleRate.set("Sample Rate: " + str(play_list.validFiles[play_list.currentSongIndex].sample_rate))
        textTotalPlayTime.set("Total Length: "+ formatTimeString(int(play_list.playTime)))
        danMode = "ON" if play_list.danthologyMode == True else "OFF"
        textDanthologyMode.set("Danthology: " + danMode)
        VolumeScale.set(play_list.VolumeLevel * 100)  # put the volume level on the scale.

    displayElementsOnPlaylist()
    updateRadioButtons()
    updateSortMenuLabel()
    progress["mode"] = play_list.ProgressBarType
    windowCascade.root.attributes('-alpha', play_list.windowOpacity)  # set the opacity
    showCurrentSongInList()

def load_directory(fpath=None):
    #this function is called when clicking on Open Directory command from menubar File menu
    global play_list
    global listBox_Song_selected_index
    if type(play_list.dirFilePath) == str:
        #if using the old version of playlist - convert the data type for this variable
        play_list.dirFilePath = list(play_list.dirFilePath)
    if fpath == None:
        play_list.dirFilePath.append(filedialog.askdirectory())
    else:
        play_list.dirFilePath.append(fpath)

    play_list.dirFilePath = list(set(play_list.dirFilePath))  # don't store duplicates
    if len(play_list.dirFilePath) > 0:
        startIndex = len(play_list.validFiles)

        #window become responsive in searchFilesInDirectories
        searchFilesInDirectories(play_list.dirFilePath[len(play_list.dirFilePath)-1])
        play_list.currentSongIndex = 0
        play_list.currentSongPosition = 0
        textFilesToPlay.set("Files: " + str(len(play_list.validFiles)))
        #displayElementsOnPlaylist() #not needed the searchFilesInDirectories also populates the listbox
        showCurrentSongInList()
        if len(play_list.validFiles) > 0:
            #window got responsive user might have operated on the play_list check again if we have
            #anything available
            SongName.set("Paused: " + play_list.validFiles[play_list.currentSongIndex].fileName)
        play_list.isListOrdered = 21 #this will mean Custom Sorting
        updateSortMenuLabel()

def searchFilesInDirectories(dir): #this function is called when loading a directory.
    #this function will scan for .mp3 files in given directory and append to the play_list any match
    #that can be played.
    global play_list
    dict_list = []
    if play_list.keepSongsStats and os.path.isfile(SongStatsFileName):
        try:
            file = open(SongStatsFileName, "rb")
            dict_list = pickle.load(file)
            file.close()
        except:
            text = ("Could not load the songs stats. File might be corrupted.")
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
    mp3FilesCausingException = ""

    scheduler.suspend_mainloop()  # we will keep window refreshed in the loop
    for root, dirs, files in os.walk(dir):
        i=0
        if scheduler.userIntervention == True:
            # user changed something in the play_list that might affect the outcome of this loop
            scheduler.userIntervention = False
            break
        for file in files:
            i+=1
            if scheduler.userIntervention == True:
                # user changed something in the play_list that might affect the outcome of this loop
                break #break from here, the break from outter loop will clear the flag
            windowCascade.root.title("Scanning " + str(root) + ": " + str(i) + " out of " + str(len(files)) + " files")
            scheduler.single_loop() # this will make the main window responsive

            if file.lower().endswith(".mp3"):
                filepath = root + "/" + file

                song = Song(filepath)
                if song.Exception == None:
                    if play_list.keepSongsStats and dict_list != []:
                        loadSongStats(song, dict_list)
                    play_list.validFiles.append(song)
                    listbox.insert(len(play_list.validFiles)-1,
                                   str(len(play_list.validFiles)-1) + ". " + song.fileName)
                    play_list.playTime += song.Length
                else:
                    mp3FilesCausingException += str(song.filePath) + "\n" + "Reason: " + str(song.Exception) + "\n\n"

    scheduler.resume_mainloop()

    if mp3FilesCausingException != "":
        text = "Unable to load the following MP3 Files: \n\n" + mp3FilesCausingException
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None),
                     windowTitle="Information")

    windowCascade.root.title(Project_Title)

def scanForNewFilesInDirectories(dir_list: list): #this function is called when loading a directory.
    #this function will scan for .mp3 files in given directory and append to the play_list any match
    #that can be played.
    global play_list
    dict_list = []
    messageForUser = ""
    added_playTime = 0
    if play_list.keepSongsStats and os.path.isfile(SongStatsFileName):
        try:
            file = open(SongStatsFileName, "rb")
            dict_list = pickle.load(file)
            file.close()
        except:
            messageForUser += ("Could not load the songs stats. File might be corrupted.")

    scheduler.suspend_mainloop()
    newFiles = []

    for element in dir_list:
        if scheduler.userIntervention == True:
            # user changed something in the play_list that might affect the outcome of this loop
            scheduler.userIntervention = False
            break
        for root, dirs, files in os.walk(element):
            i=0
            if scheduler.userIntervention == True:
                # user changed something in the play_list that might affect the outcome of this loop
                break #the break from outter loop will clear the flag
            for file in files:
                i+=1
                if scheduler.userIntervention == True:
                    # user changed something in the play_list that might affect the outcome of this loop
                    break #the break from outter loop will clear the flag
                windowCascade.root.title("Scanning " + str(root) + ": " + str(i) + " out of " + str(len(files)) + " files")
                scheduler.single_loop() # this will make the main window responsive
                if file.lower().endswith(".mp3"):
                    filepath = root + "/" + file

                    song = Song(filepath)
                    if song.Exception == None and song not in play_list.validFiles  and song not in newFiles:
                        if play_list.keepSongsStats and dict_list != []:
                            loadSongStats(song, dict_list)
                        newFiles.append(song)
                        added_playTime += song.Length
                        messageForUser += "New File: " + str(song.filePath) + "\n\n"
                    elif song.Exception != None and song not in play_list.validFiles  and song not in newFiles:
                        messageForUser += "Invalid New File: " + str(song.filePath) + "\n" + \
                                          "Reason: " + str(song.Exception) + "\n\n"

    scheduler.resume_mainloop()

    windowCascade.root.title(Project_Title)
    return messageForUser, newFiles, added_playTime

def play_music():
    """
    This function sets up the mixer and initializes all needed parties based on data collected
    from the mp3. file. In this function the playback starts hearing.
    """
    global play_list
    global visualSongNameLabel
    global s_rate
    global channels
    global temp_SongEndPos
    global Project_Title
    global flagged_files_looped_consecutively
    if len(play_list.validFiles) > 0 and play_list.currentSongIndex!=None:
        if (hasattr(play_list.validFiles[play_list.currentSongIndex], "Exception") == False):
            setattr(play_list.validFiles[play_list.currentSongIndex], "Exception", None)
        if(play_list.validFiles[play_list.currentSongIndex].Exception == None):
            #if the .mp3 file is flagged to cause Exception we will not attempt to play it
            try:
                if s_rate != play_list.validFiles[play_list.currentSongIndex].sample_rate or channels != play_list.validFiles[play_list.currentSongIndex].channels \
                        or s_rate == None or channels == None:
                    s_rate = play_list.validFiles[play_list.currentSongIndex].sample_rate
                    channels = play_list.validFiles[play_list.currentSongIndex].channels
                    if pygame.mixer.get_init():
                        pygame.mixer.quit() # quit it, to make sure it is reinitialized
                        pygame.mixer.pre_init(frequency=s_rate, size=-16, channels=channels, buffer=4096)
                    else:
                        pygame.mixer.pre_init(frequency=s_rate, size=-16, channels=channels, buffer=4096)
                    pygame.mixer.init()
                if play_list.useCrossFade == True and play_list.currentSongPosition <= play_list.validFiles[play_list.currentSongIndex].startPos :
                    #let the next song start from seconds stored in play_list.crossFadeGap
                    play_list.currentSongPosition = play_list.crossFadeGap

                    play_list.validFiles[play_list.currentSongIndex].fadein_duration = play_list.crossFadeDuration
                    play_list.validFiles[play_list.currentSongIndex].fadeout_duration = play_list.crossFadeDuration
                    temp_SongEndPos = play_list.validFiles[play_list.currentSongIndex].endPos
                    play_list.validFiles[play_list.currentSongIndex].endPos = (play_list.validFiles[play_list.currentSongIndex].Length - play_list.crossFadeGap*3)
                if (play_list.validFiles[play_list.currentSongIndex].fadein_duration == 0  \
                        or play_list.currentSongPosition > play_list.validFiles[play_list.currentSongIndex].fadein_duration):
                    pygame.mixer.music.set_volume(play_list.VolumeLevel) # you can set the Volume
                else: # enter here if song uses fadein
                    pygame.mixer.music.set_volume(0.0) #the volume will start from 0.0 and will increase progressively
                if listBox_Song_selected_index != None and len(searchValue.get()) == 0: #ignore this statement if Search is being used
                    if listBox_Song_selected_index != play_list.currentSongIndex:
                        play_list.currentSongIndex = listBox_Song_selected_index
                        play_list.currentSongPosition = play_list.validFiles[play_list.currentSongIndex].startPos
                        play_list.RESUMED = False
                elif listBox_Song_selected_index == play_list.currentSongIndex and len(searchValue.get()) == 0: #ignore this statement if Search is being used:
                    if play_list.danthologyMode == False:
                        play_list.currentSongPosition=0
                    #otherwise keep the currentSongPosition from the previous one.
                pygame.mixer.music.load(play_list.validFiles[play_list.currentSongIndex].filePath)
                pygame.mixer.music.play()
                PausedButtonText.set("Pause")
                play_list.isSongPause = False
                if play_list.danthologyDuration == 0 and play_list.danthologyMode: #start song from the beginning.
                    play_list.currentSongPosition = play_list.validFiles[play_list.currentSongIndex].startPos
                if play_list.currentSongPosition > 0:
                    pygame.mixer.music.set_pos(play_list.currentSongPosition)
                    play_list.RESUMED = True
                elif play_list.validFiles[play_list.currentSongIndex].startPos > 0:
                    start_pos = play_list.validFiles[play_list.currentSongIndex].startPos
                    if play_list.currentSongPosition == 0:
                        if play_list.danthologyMode == False:
                            play_list.currentSongPosition = start_pos
                        # otherwise keep the currentSongPosition from the previous one.
                    pygame.mixer.music.set_pos(start_pos)
                    play_list.RESUMED = True
                if play_list.danthologyDuration > 0 and play_list.danthologyMode:
                    play_list.danthologyTimer = time.time()
            except Exception as e:
                flagged_files_looped_consecutively+=1
                SongName.set("Flagged: " + play_list.validFiles[play_list.currentSongIndex].fileName)
                play_list.validFiles[play_list.currentSongIndex].refreshSongData() #this will flag the .mp3 file as not playable
                text = ("Play Music Function: \n" + str(e))
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
            else:
                SongName.set("Playing: " + play_list.validFiles[play_list.currentSongIndex].fileName)
                SongSize.set("Size: " + str(play_list.validFiles[play_list.currentSongIndex].fileSize) + " MB")
                songLength = float("{0:.0f}".format(play_list.validFiles[play_list.currentSongIndex].Length))  # no decimals needed
                textLength.set("Length: "+ formatTimeString(songLength))
                textGenre.set("Genre: " + str(play_list.validFiles[play_list.currentSongIndex].Genre))
                textArtist.set("Artist: " + str(play_list.validFiles[play_list.currentSongIndex].Artist))
                textAlbum.set("Album: " + str(play_list.validFiles[play_list.currentSongIndex].Album))
                textTitle.set("Title: " + str(play_list.validFiles[play_list.currentSongIndex].Title))
                textYear.set("Year: " + str(play_list.validFiles[play_list.currentSongIndex].Year))
                textSongListenedTime.set("Played time: " + formatTimeString(int(play_list.validFiles[play_list.currentSongIndex].SongListenedTime)))
                startPos = int(play_list.validFiles[play_list.currentSongIndex].startPos)
                textStartTime.set("Starts at: " + formatTimeString(startPos))
                endPos = int(play_list.validFiles[play_list.currentSongIndex].endPos)
                textEndTime.set("Ends at: " + formatTimeString(endPos))
                textFadeIn.set("FadeIn: " + str(play_list.validFiles[play_list.currentSongIndex].fadein_duration)+"s")
                textFadeOut.set("FadeOut: " + str(play_list.validFiles[play_list.currentSongIndex].fadeout_duration) +"s")
                mode = "Stereo" if play_list.validFiles[play_list.currentSongIndex].channels == 2 else "Mono"
                textMonoStereoMode.set("Mode: " + mode)
                textSampleRate.set("Sample Rate: " + str(play_list.validFiles[play_list.currentSongIndex].sample_rate))
                progress["maximum"] = play_list.validFiles[play_list.currentSongIndex].Length
                songRating.set(str(play_list.validFiles[play_list.currentSongIndex].Rating))
                if play_list.playingFileNameTransition == "none":
                    visualSongNameLabel = play_list.validFiles[play_list.currentSongIndex].fileName
                elif play_list.playingFileNameTransition == "typewriting":
                    visualSongNameLabel = ""
                elif play_list.playingFileNameTransition == "separation":
                    visualSongNameLabel = "_" + play_list.validFiles[play_list.currentSongIndex].fileName
                updateRadioButtons()
                #Make Window Title the song being currently played:
                if play_list.useSongNameTitle:
                    Project_Title = "   " + play_list.validFiles[play_list.currentSongIndex].fileName + "   "
                    windowCascade.root.title(Project_Title)
                play_list.validFiles[play_list.currentSongIndex].NumberOfPlays+=1
                textNofPlays.set("No. of Plays: " + str(play_list.validFiles[play_list.currentSongIndex].NumberOfPlays))
                flagged_files_looped_consecutively = 0
        else:
            #when the .mp3 file is flagged as not playable, we will attempt to refresh to see whatever problems
            #it had are now fixed
            SongName.set("Flagged: " + play_list.validFiles[play_list.currentSongIndex].fileName)
            flagged_files_looped_consecutively += 1
            play_list.validFiles[play_list.currentSongIndex].refreshSongData()  # this will flag the .mp3 file as not playable

def pause_music(): #this function is called when clicking on Play/Pause Button.
    #this function will determine whether we're meant play or pause the song
    global play_list
    if pygame.mixer.get_init(): #if the mixer is initialized it means music is loaded in the playback either currently playing, paused or stopped.
        try:
            if play_list.validFiles[play_list.currentSongIndex].Exception != None:
                #allow to stop looping if file became invalid
                stop_music()
            elif play_list.isSongPause == False and pygame.mixer.music.get_busy(): #Music is currently playing
                pygame.mixer.music.pause()
                PausedButtonText.set("Play")
                play_list.isSongPause = True
                if len(play_list.validFiles) > 0 :
                    SongName.set("Paused: " + play_list.validFiles[play_list.currentSongIndex].fileName)
                else:
                    SongName.set("Paused: ")
            elif play_list.isSongPause == True and pygame.mixer.music.get_busy(): #Music is currently paused
                pygame.mixer.music.unpause()
                PausedButtonText.set("Pause")
                play_list.isSongPause = False
                if len(play_list.validFiles) > 0:
                    SongName.set("Playing: " + play_list.validFiles[play_list.currentSongIndex].fileName)
                else:
                    SongName.set("Playing: ")
            elif pygame.mixer.music.get_busy() == False: #Music is currently stopped and playback is free
                play_music()
        except Exception as e:
            text = ("Pause Music Function: \n" + str(e))
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
    else: #playback is free, mixer is not initialized.
        play_music()

def stop_music(): #this function is called when clicking on Stop Button.
    #this will stop the playback
    global play_list
    if pygame.mixer.get_init():
        try:
            if pygame.mixer.music.get_busy():
                #stop the music if possible else only clear the labels and stop looping
                pygame.mixer.music.stop()
            else:
                if (hasattr(play_list.validFiles[play_list.currentSongIndex], "Exception") == False):
                    setattr(play_list.validFiles[play_list.currentSongIndex], "Exception", None)
                if play_list.validFiles[play_list.currentSongIndex].Exception != None:
                    #enter here on invalid files
                    pygame.mixer.quit()
            SongName.set("Playing: ")
            progress["value"] = 0
            textLength.set("Length: ")
            textGenre.set("Genre: ")
            textAlbum.set("Album: ")
            textYear.set("Year: ")
            textTitle.set("Title: ")
            textArtist.set("Artist: ")
            textNofPlays.set("No. of Plays: ")
            textEndTime.set("Ends at: ")
            textStartTime.set("Starts at: ")
            textMonoStereoMode.set("Mode: ")
            textFadeIn.set("FadeIn: ")
            textFadeOut.set("FadeOut: ")
            textSampleRate.set("Sample Rate: ")
            if play_list.progressTime == "Ascending":
                textProgress.set("Time Elapsed: ")
            else:
                textProgress.set("Time Left: ")
            SongSize.set("Size: ")
            if play_list.danthologyMode == False:
                play_list.currentSongPosition=0
            play_list.RESUMED = False
            PausedButtonText.set("Play")
            play_list.isSongPause = False
            play_list.isSongStopped = True
        except Exception as e:
            text = ("Stop Music Function: \n" + str(e))
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")

def handleDanthology(): #this function is called when changing a song, with DanthologyMode enabled.
    #Dantology means we maintain the same playback position from current song to the next one
    #this will act as mix or song previews
    global play_list
    if play_list.currentSongPosition >= math.floor(play_list.validFiles[play_list.currentSongIndex].endPos):
        play_list.currentSongPosition = 0
    else:
        if play_list.RESUMED:
            play_list.currentSongPosition = math.floor(play_list.currentSongPosition + pygame.mixer.music.get_pos() / 1000)
        else:
            play_list.RESUMED = True

def next_song(): #this function is called when clicking on Next Button.
    # here we set up the playback to that it will play the next song selection
    global listBox_Song_selected_index
    global play_list
    if flagged_files_looped_consecutively < FLAGGED_MAXIMUM_ITERATIONS:
        #in case of invalid files only loop through it for FLAGGED_MAXIMUM_ITERATIONS times
        if len(searchValue.get()) == 0:
            if len(play_list.validFiles) > 0 and play_list.currentSongIndex!=None:
                if (play_list.SHUFFLE==False):
                    try:
                        play_list.currentSongIndex+=1
                        if play_list.currentSongIndex >= len(play_list.validFiles):
                            if play_list.REPEAT==3: #End of playlist, do not repeat.
                                play_list.currentSongIndex = len(play_list.validFiles)-1 #last file on playlist
                                stop_music()
                                clearLabels()
                                return #silence must be heard.
                            else:
                                play_list.currentSongIndex = 0
                        else:
                            pass
                    except Exception as exp:
                        text = ("Next Song Function: \n" + str(exp))
                        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
                else:
                    play_list.shufflingHistory.append(play_list.currentSongIndex)
                    if shuffling_playlist() == False:
                        play_list.currentSongIndex = 0
                        stop_music()
                        clearLabels()
                        play_list.shufflingHistory=[] # this will enable restart on this pattern.
                        return #stop it here, playlist has ended.
                listBox_Song_selected_index = play_list.currentSongIndex #without this the song will not change
                if play_list.danthologyMode == False:
                    play_list.currentSongPosition=0
                else:
                    handleDanthology()
                showCurrentSongInList()
                play_music()
        else:
            playNextSearchItem()
    else:
        stop_music()

def previous_song(): #this function is called when clicking on Previous Button.
    #here we set up the playback to that it will play the previous song selection
    global listBox_Song_selected_index
    global play_list
    if len(searchValue.get()) == 0:
        if len(play_list.validFiles) > 0 and play_list.currentSongIndex!=None:
            if(play_list.SHUFFLE==False):
                try:
                    play_list.currentSongIndex -= 1
                    if play_list.currentSongIndex < 0:
                        play_list.currentSongIndex = len(play_list.validFiles)-1
                    else:
                        pass
                except Exception as exp:
                    text = ("Previous Song Function: \n" + str(exp))
                    WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
            else:
                if len(play_list.shufflingHistory) > 0 :
                    play_list.currentSongIndex = play_list.shufflingHistory[len(play_list.shufflingHistory)-1] # load the last item added to history.
                    del play_list.shufflingHistory[len(play_list.shufflingHistory)-1] #remove from history the song which was loaded.
            listBox_Song_selected_index = play_list.currentSongIndex #without this the song will not change
            if play_list.danthologyMode == False:
                play_list.currentSongPosition = 0
            else:
                handleDanthology()
            showCurrentSongInList()
            play_music()
            # play_music() function should always be called last.
            # As this function triggers a scheduler which will only end during pause or stop
            # statements placed ater play_music will not be executed until scheduler ends which
            # produces huge delays in their execution
    else:
        playPreviousSearchItem()

def addFontTransitions():
    #this function is handling font transitions based on user preferences set from Customize window
    global visualSongNameLabel
    global Project_Title
    if play_list.usePlayerTitleTransition:
        Project_Title = fontTitleTransition(Project_Title)
        windowCascade.root.title(Project_Title)  # add animation to font when playing music
    if play_list.playingFileNameTransition == "typewriting":
        visualSongNameLabel = fontTypeWritingTransition(visualSongNameLabel)
    elif play_list.playingFileNameTransition == "separation":
        visualSongNameLabel = fontSeparatedTransition(visualSongNameLabel)
    SongName.set("Playing: " + visualSongNameLabel)

def makeProgress(value):
    #this function is called frmo view_progress() this will also be called once every ProgressRealTime seconds
    #here we monitor the playback progress and update all relevant Main Window elements
    #we determine actions when playback ends
    global progress
    global play_list
    if play_list.progressTime == "Ascending":
        textProgress.set("Time Elapsed: " + formatTimeString(value))
    else:
        SongLength = int(play_list.validFiles[play_list.currentSongIndex].Length - value)
        textProgress.set("Time Left: " + formatTimeString(SongLength))

    progress["value"] = value

    if play_list.VolumeLevel > 0.0:  # only if Volume not Muted means listening to it.
        play_list.validFiles[
            play_list.currentSongIndex].SongListenedTime += calculateListenedTimeSinceLastIter(value)  # if entered here, means song is playing with volume!=0
        play_list.PlaylistListenedTime += calculateListenedTimeSinceLastIter(value)  # if entered here, means song is playing with volume!=0
        textSongListenedTime.set(
            "Played time: " + formatTimeString(
                play_list.validFiles[play_list.currentSongIndex].SongListenedTime))
        textPlaylistListenedTime.set(
            "Total listening time: " + formatTimeString(play_list.PlaylistListenedTime))

    if play_list.validFiles[play_list.currentSongIndex].fadein_duration > 0:
        if value <= play_list.validFiles[play_list.currentSongIndex].fadein_duration + 1:
            fadein(value - play_list.validFiles[play_list.currentSongIndex].startPos)
    if play_list.validFiles[play_list.currentSongIndex].fadeout_duration > 0:
        if value >= play_list.validFiles[play_list.currentSongIndex].endPos - \
                play_list.validFiles[play_list.currentSongIndex].fadeout_duration:
            if play_list.useCrossFade:
                fadeout(play_list.validFiles[play_list.currentSongIndex].endPos - value + play_list.crossFadeGap)
                # delay fadeout, song should end with 0.3 volume, same volume the next one is supposed to start
            else:
                fadeout(play_list.validFiles[play_list.currentSongIndex].endPos - value)
    if play_list.danthologyMode and play_list.danthologyDuration > 0:
        if time.time() - play_list.danthologyTimer > play_list.danthologyDuration:
            # Danthology
            next_song()
    if value >= math.floor(play_list.validFiles[play_list.currentSongIndex].endPos):
        if play_list.useCrossFade:  # hurry things up if using crossfade, so there will be no gaps between tracks
            play_list.validFiles[play_list.currentSongIndex].fadein_duration = 0
            play_list.validFiles[play_list.currentSongIndex].fadeout_duration = 0
            if temp_SongEndPos != None:
                play_list.validFiles[play_list.currentSongIndex].endPos = temp_SongEndPos
            else:  # this should never happen.
                play_list.validFiles[play_list.currentSongIndex].endPos = play_list.validFiles[
                    play_list.currentSongIndex].Length

            if play_list.REPEAT == 1 or play_list.REPEAT == 3:
                next_song()
            elif play_list.REPEAT == 0:  # Repeat Off
                stop_music()
                clearLabels()
            else:  # play_list.REPEAT==2 means Repeat One
                play_list.RESUMED = False
                play_list.currentSongPosition = 0
                play_music()  # play the same song again.

        else:
            stop_music()
            play_list.isSongPause = False
            play_list.isSongStopped = False  # song is not stopped in this circumstances, song has finished
            # Playback will take 1 second break before next song.

gifImageObjectFrame = 0 #NOT USED
def animateGifImageBackground(): #NOT USED
    #this function should have been used to handle gif background in the Main Window
    global gifImageObjectFrame
    if play_list.skin_theme.background_image != None and ".gif" in play_list.skin_theme.background_image:
        imageObject = Image.open(play_list.skin_theme.background_image)
        if imageObject.is_animated:
            imageObject.seek(gifImageObjectFrame)
            background_image = ImageTk.PhotoImage(imageObject)
            background_label.configure(image=background_image)
            background_label.image = background_image
            gifImageObjectFrame+=1
            if gifImageObjectFrame >= imageObject.n_frames:
                gifImageObjectFrame = 0

def viewProgress(): #this function is a scheduler called once every progressRealTime seconds
    #this function will deal with Main Window updates and will respond to every user action.
    #It will act as an infinite loop as long as Main Window is opened.
    global play_list
    global nextSongTrigger
    global previousSongTrigger

    if play_list.usingSlideShow == True and windowCascade.Slideshow != None:
        windowCascade.Slideshow.countSeconds()

    if SleepingTool.timer > 0:
        SleepingTool.whenIsEvent()

    checkReadDataFromSharedMemory()
    #Check if any hotkeys trigger events
    if hotkeyMonitor.playPauseTrigger == True:
        hotkeyMonitor.playPauseTrigger = False
        pause_music()
    if hotkeyMonitor.nextSongTrigger == True:
        hotkeyMonitor.nextSongTrigger = False
        next_song()
    if hotkeyMonitor.previousSongTrigger == True:
        hotkeyMonitor.previousSongTrigger = False
        previous_song()

    #Deal with the music and window
    if pygame.mixer.get_init():
        if pygame.mixer.music.get_busy() and play_list.isSongPause == False: # Music is currently playing
            addFontTransitions()
            if play_list.RESUMED:
                local_position = play_list.currentSongPosition + pygame.mixer.music.get_pos() / 1000
                makeProgress(local_position)
            else:
                play_list.currentSongPosition = pygame.mixer.music.get_pos()/1000
                makeProgress(play_list.currentSongPosition)

        elif pygame.mixer.music.get_busy() == False and play_list.isSongPause == False and play_list.isSongStopped == False:
            #song has ended
            play_list.RESUMED = False
            if (play_list.REPEAT == 1 or play_list.REPEAT == 3):
                #if repead all or repeat none
                next_song()  # this will keep repeating the playlist
            elif play_list.REPEAT == 2:
                #if repeat one
                play_music()  # this will repeat the current song
            else:
                #if repeat off
                play_list.isSongStopped = True

    windowCascade.root.update()  # Force an update of the GUI

def volume_down(): #this function is called when changing Volume from Keyboard using < key
    global play_list
    if pygame.mixer.get_init():
        play_list.VolumeLevel-=0.1
        if (play_list.VolumeLevel < 0.0):
            play_list.VolumeLevel = 0.0
        if play_list.currentSongPosition - play_list.validFiles[play_list.currentSongIndex].startPos > \
                play_list.validFiles[play_list.currentSongIndex].fadein_duration and play_list.currentSongPosition < \
                play_list.validFiles[play_list.currentSongIndex].endPos - play_list.validFiles[play_list.currentSongIndex].fadeout_duration:
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
        VolumeScale.set(play_list.VolumeLevel*100)

def volume_up(): #this function is called when changing Volume from Keyboard using > key
    global play_list
    if pygame.mixer.get_init():
        play_list.VolumeLevel+=0.1
        if(play_list.VolumeLevel>1.0):
            play_list.VolumeLevel=1.0
        if play_list.currentSongPosition - play_list.validFiles[play_list.currentSongIndex].startPos > \
            play_list.validFiles[play_list.currentSongIndex].fadein_duration and play_list.currentSongPosition < \
                play_list.validFiles[play_list.currentSongIndex].endPos - play_list.validFiles[play_list.currentSongIndex].fadeout_duration:
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
        VolumeScale.set(play_list.VolumeLevel * 100)

def shuffle(): #this function is called when clicking on SHUFFLE Button.
    global play_list
    if(play_list.SHUFFLE):
        ShuffleButtonText.set("Shuffle Off")
        play_list.SHUFFLE = False
        play_list.shufflingHistory = [] #empty the history
    else:
        ShuffleButtonText.set("Shuffle On")
        play_list.SHUFFLE = True

def shuffling_playlist():
    #this function is called from shuffle() to ensure that we keep track of the playback history
    #and to handle the repeat in the wsy the user wants to
    global play_list
    if len(play_list.validFiles) > 1:
        if play_list.REPEAT == 3: #Repeat None - means play each song only once
            validFiles_indexes = list (range(len(play_list.validFiles))) # create a list of indexes for the valid files
            unique_elements = list(set(validFiles_indexes).difference(set(play_list.shufflingHistory))) #make a list of elements that were never played.
            if len(unique_elements) > 0: # if elements that never played
                rand = random.randint(0, len(unique_elements)-1) #get a random element - endpoints included
                choice = unique_elements[rand]
                play_list.currentSongIndex = choice
            else:
                #here we need to stop it, because we reached end of playlist. Every song in the playlist was played.
                return False
        else: # you can play same song multiple times
            rand = random.randint(0, len(play_list.validFiles)-1) #get a random element - endpoints included
            play_list.currentSongIndex = rand
        return True

def save_playlist(): #this function is called when clicking on Save Playlist as
    global play_list
    windowCascade.root.filename = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                 filetypes=(("pypl files", "*.pypl"), ("all files", "*.*")))
    if windowCascade.root.filename:
        if ".pypl" in windowCascade.root.filename:
            file = open(windowCascade.root.filename, "wb")
        else:
            file = open(windowCascade.root.filename + ".pypl", "wb")
        if pygame.mixer.get_init():
            if play_list.RESUMED:
                play_list.currentSongPosition += math.floor(pygame.mixer.music.get_pos() / 1000)
            else:
                play_list.currentSongPosition = math.floor(pygame.mixer.music.get_pos() / 1000)
        pickle.dump(play_list, file)
        file.close()

def clearLabels():
    #this function is called on Clear Playlist on Stop Button, or at the end of the playlist.
    textFilesToPlay.set("Files: " + str(len(play_list.validFiles)))
    VolumeScale.set(play_list.VolumeLevel * 100)
    textGenre.set("Genre: ")
    textArtist.set("Artist: ")
    SongName.set("Playing: ")
    textAlbum.set("Album: ")
    textTitle.set("Title: ")
    textYear.set("Year: ")
    textSongListenedTime.set("Played time: ")
    textPlaylistListenedTime.set("Total listening time: ")
    textFadeIn.set("FadeIn: ")
    textFadeOut.set("FadeOut: ")
    SongSize.set("Size: ")
    textMonoStereoMode.set("Mode: ")
    textNofPlays.set("No. of Plays: ")
    danMode = "OFF" if play_list.danthologyMode==False else "ON"
    textDanthologyMode.set("Danthology: " + danMode)
    textSampleRate.set("Sample Rate: ")
    textEndTime.set("Ends at: ")
    textStartTime.set("Starts at: ")
    textLength.set("Length: ")
    if play_list.progressTime == "Ascending":
        textProgress.set("Time Elapsed: ")
    else:
        textProgress.set("Time Left: ")

def savingSongStats(): #this function is called when canceling the window to ensure we save songStats
    dict_list = []
    dictionary = {}
    try:
        if os.path.isfile(SongStatsFileName):
            file = open(SongStatsFileName, "rb")
            dict_list = pickle.load(file)
            file.close()
    except:
        text = ("Could not load the songs stats. File might be corrupted.\nI will create a new one.")
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")
        dict_list = [] #make sure this is empty
        dictionary = {} #make sure this is empty

        scheduler.suspend_mainloop()  # we will keep window refreshed in the loop
        for song in play_list.validFiles:
            # This loop can continue its work even under user intervention flag
            # since this is executed before clearing the play_list content
            windowCascade.root.title("Saving Songs Stats: " + str(play_list.validFiles.index(song)) + " out of " + str(len(play_list.validFiles) ))
            scheduler.single_loop() # this will make the main window responsive
            dictionary ["fileName"] = song.fileName
            dictionary ["Rating"] = song.Rating
            dictionary ["NumberOfPlays"] = song.NumberOfPlays
            dictionary ["fadein_duration"] = song.fadein_duration
            dictionary ["fadeout_duration"] = song.fadeout_duration
            dictionary ["endPos"] = song.endPos
            dictionary ["startPos"] = song.startPos
            dictionary ["SongListenedTime"] = song.SongListenedTime
            dict_list.append(dictionary)
            dictionary = {}
        scheduler.resume_mainloop()
    else:
        scheduler.suspend_mainloop()
        for song in play_list.validFiles:
            #This loop can continue its work even under user intervention flag
            # since this is executed before clearing the play_list content
            windowCascade.root.title("Saving Songs Stats: " + str(play_list.validFiles.index(song)) + " out of " + str(len(play_list.validFiles) ))
            scheduler.single_loop() # this will make the main window responsive
            dictionary ["fileName"] = song.fileName
            dictionary ["Rating"] = song.Rating
            dictionary ["NumberOfPlays"] = song.NumberOfPlays
            dictionary ["fadein_duration"] = song.fadein_duration
            dictionary ["fadeout_duration"] = song.fadeout_duration
            dictionary ["endPos"] = song.endPos
            dictionary ["startPos"] = song.startPos
            dictionary ["SongListenedTime"] = song.SongListenedTime
            ifDuplicate = [element for element in dict_list if element['fileName'] == song.fileName]
            #print("Value of duplicate: " + str(ifDuplicate[0]["fileName"].encode("utf-8")))
            if ifDuplicate != []:
                del dict_list[dict_list.index(ifDuplicate[0])]
                #print("Found duplicate: " + str(ifDuplicate[0]["fileName"].encode("utf-8")))
            dict_list.append(dictionary)
            dictionary = {}
        scheduler.resume_mainloop()
    windowCascade.root.title(Project_Title)
    file = open(SongStatsFileName, "wb")
    pickle.dump(dict_list, file)
    file.close()

def loadSongStats(song: Song, dict_list: list): #this function is called when loading songs to a playlist if MaintainSongsStats is true
    global play_list
    existedItem = [element for element in dict_list if element['fileName'] == song.fileName]
    if existedItem != []:
        existedItem = existedItem[0] # the list should only contain one element
        if existedItem["Rating"] > song.Rating: #will solve duplicates
            song.Rating = existedItem["Rating"]
        if existedItem["NumberOfPlays"] > song.NumberOfPlays: #will solve duplicates
            song.NumberOfPlays += existedItem["NumberOfPlays"]
        song.fadein_duration = existedItem ["fadein_duration"]
        song.fadeout_duration = existedItem ["fadeout_duration"]
        song.endPos = existedItem ["endPos"]
        song.startPos = existedItem ["startPos"]
        if existedItem["SongListenedTime"] > song.SongListenedTime: #will solve duplicates
            song.SongListenedTime = existedItem["SongListenedTime"]
        play_list.PlaylistListenedTime += song.SongListenedTime # calculating playlistListenedTime

def new_playlist(): #this function is called when clicking clearing the playlist from menubar / File Menu
    global play_list
    global listBox_Song_selected_index
    global scheduler

    if scheduler.isMainLoopSuspended == True:
        #when scheduler is cancelled we might be in a loop iterating through play_list files
        #the new_playlist() also handles removing everything within the playlist
        scheduler.userIntervention = True #by setting this to true we can break the current operation
        #before clearing the playlist
    savingSongStats() #saving song stats.
    if pygame.mixer.get_init():
        if pygame.mixer.music.get_busy():
            WindowDialog() #predefined window dialog
        else:
            if play_list.resetSettings == False:
                play_list.isSongPause = False
                play_list.isSongStopped = False
                play_list.dirFilePath = []
                play_list.validFiles = []
                play_list.currentSongIndex = None
                play_list.currentSongPosition = 0
                play_list.RESUMED=False
                play_list.playTime = 0
                play_list.shufflingHistory = []
                play_list.isListOrdered = 21 #this will mean Custom Sorting
                play_list.PlaylistListenedTime = 0
                play_list.BornDate = datetime.datetime.now()
            else:
                play_list = Playlist()
                # Restore default skin
                play_list.skin_theme.changingSkin()
                windowCascade.root.attributes('-alpha', play_list.windowOpacity)
            clearLabels()
            # displayElementsOnPlaylist()
            listbox.delete(0, tk.END)
            listBox_Song_selected_index = None
    else:
        if play_list.resetSettings == False:
            play_list.isSongPause = False
            play_list.isSongStopped = False
            play_list.dirFilePath = []
            play_list.validFiles = []
            play_list.currentSongIndex = None
            play_list.currentSongPosition = 0
            play_list.RESUMED=False
            play_list.playTime = 0
            play_list.shufflingHistory = []
            play_list.isListOrdered = 21 #this will mean Custom Sorting
            play_list.PlaylistListenedTime = 0
            play_list.BornDate = datetime.datetime.now()
        else:
            play_list = Playlist()
            windowCascade.root.attributes('-alpha', play_list.windowOpacity)
            # Restore default skin
            play_list.skin_theme.changingSkin()
        listBox_Song_selected_index=None
        clearLabels()
        textTotalPlayTime.set("Total Length: " + formatTimeString(int(play_list.playTime)))
        # displayElementsOnPlaylist()
        listbox.delete(0, tk.END)

def updateSortMenuLabel(): #this function will update the sort menu labels
    # play_list.isListOrdered value : 0-By Filename ; 1-By Filename Reversed 2-Randomized; 3-By Rating etc.
    resetSortMenuLabels()
    if play_list.isListOrdered <= 20: #if list not ordered Custom
        if hasattr(menubar, "preferences_sort_menu"):
            menubar.preferences_sort_menu.entryconfigure(play_list.isListOrdered, label = menubar.selectedToken + menubar.preferences_sort_menu.entrycget(play_list.isListOrdered, "label"))

def elementPlaylistDoubleClicked(event): #function called on double-click event within the listbox
    global play_list
    if listbox.size():
        if len(searchValue.get()) == 0:
            widget = event.widget
            index = int(widget.curselection()[0])
            #value = widget.get(index)
            play_list.currentSongIndex = index
            if play_list.danthologyMode == False: #else will let the next song continue where this one left
                play_list.currentSongPosition = play_list.validFiles[play_list.currentSongIndex].startPos
            elif pygame.mixer.get_init():
                play_list.currentSongPosition += math.floor(pygame.mixer.music.get_pos() / 1000)
            play_music()
        else:
            widget = event.widget
            index = int(widget.curselection()[0])
            value = widget.get(index)
            value=value.split(". ")
            play_list.currentSongIndex = int(value[0])
            if play_list.danthologyMode == False: #else will let the next song continue where this one left
                play_list.currentSongPosition = play_list.validFiles[play_list.currentSongIndex].startPos
            elif pygame.mixer.get_init():
                play_list.currentSongPosition += math.floor(pygame.mixer.music.get_pos() / 1000)
            play_music()

def readjustSearchFormWidth():
    # calculating the proper width for the search form so that it will always have same
    # width as the listbox
    SearchFormWidth = labelSearch.winfo_reqwidth() + ClearSearchButton.winfo_reqwidth() + searchValue.winfo_reqwidth()
    diff = listbox.winfo_reqwidth() + scroll.winfo_reqwidth()
    diff -= SearchFormWidth
    diff = diff / calculateLetterWidthPixels()
    searchValue["width"] += int(diff)

def displayElementsOnPlaylist(): #this function will display playlist elements in the listbox
    global listbox
    mainWindowUpdate() #this will make the window more responsive
    listbox.delete(0, tk.END)

    lst = []

    #scheduler.suspend_mainloop() # this is not needed the user will not see the changes we updated the window before removing the listbox
    for index in range(0, len(play_list.validFiles)):
        lst.append(str(index) + ". " + play_list.validFiles[index].fileName)
        if hasattr(play_list.validFiles[index], "bitrate") == False:
            setattr(play_list.validFiles[index], "bitrate", "unknown")
        #scheduler.single_loop()

    listbox.insert(tk.END, *lst)
    #scheduler.resume_mainloop()

    textTotalPlayTime.set("Total Length: " + formatTimeString(int(play_list.playTime)))
    if play_list.viewModel == "PLAYLIST":
        changePlaylistView() # this will readjust the window.

def changingBackgroundElementColor(event):
    global labelTextColor
    global play_list
    #this function will handle the change of custom background color to all elements

    #changing buttons
    PauseButton["bg"]=SkinColor.get()
    StopButton["bg"]=SkinColor.get()
    NextButton["bg"]=SkinColor.get()
    PreviousButton["bg"]=SkinColor.get()
    ShuffleButton["bg"]=SkinColor.get()
    RepeatButton["bg"]=SkinColor.get()
    ClearSearchButton["bg"]=SkinColor.get()

    #changing listbox
    listbox["bg"]=SkinColor.get()
    listbox["selectforeground"] = SkinColor.get()
    ListboxFrame["bg"]=SkinColor.get()
    SearchForm["bg"]=SkinColor.get()
    SearchFrame["bg"]=SkinColor.get()
    labelSearch["bg"]=SkinColor.get()

    #changing style for progressbar and scrollbar:
    progress_style.configure("Horizontal.TProgressbar", background = SkinColor.get(), bordercolor=SkinColor.get())
    scroll_style.configure("Vertical.TScrollbar", background=SkinColor.get(), bordercolor=SkinColor.get())
    volume_scale_style.configure('Vertical.TScale', background=SkinColor.get(), bordercolor=SkinColor.get(),
                                 lightcolor=SkinColor.get(), darkcolor=SkinColor.get())

    #changing labels
    if play_list.skin_theme.unique_font_color != True:
        searchValue["fg"] = SkinColor.get()
        labelPlaying["fg"]=SkinColor.get()
        labelProgress["fg"]=SkinColor.get()
        labelSize["fg"]=SkinColor.get()
        labelFilesToPlay["fg"]=SkinColor.get()
        labelLength["fg"]=SkinColor.get()
        labelGenre["fg"]=SkinColor.get()
        labelStartTime["fg"]=SkinColor.get()
        labelEndTime["fg"]=SkinColor.get()
        labelTotalPlayTime["fg"]=SkinColor.get()
        labelSleepTimer["fg"]=SkinColor.get()
        labelWakeTimer["fg"]=SkinColor.get()
        labelFadeIn["fg"]=SkinColor.get()
        labelFadeOut["fg"]=SkinColor.get()
        labelMonoStereoMode["fg"]=SkinColor.get()
        labelSampleRate["fg"]=SkinColor.get()
        labelNofPlays["fg"]=SkinColor.get()
        labelDanthologyMode["fg"]=SkinColor.get()
        labelArtist["fg"]=SkinColor.get()
        labelAlbum["fg"]=SkinColor.get()
        labelTitle["fg"]=SkinColor.get()
        labelSongListenedTime["fg"]=SkinColor.get()
        labelPlaylistListenedTime["fg"]=SkinColor.get()
        labelYear["fg"]=SkinColor.get()
        listbox.configure(selectforeground=SkinColor.get())
        progress_style.configure("Horizontal.TProgressbar", troughcolor=labelBackground.get())
        scroll_style.configure("Vertical.TScrollbar", troughcolor=labelBackground.get())
        volume_scale_style.configure('Vertical.TScale', troughcolor=labelBackground.get())
        labelTextColor = SkinColor.get()

    if windowCascade.Customize != None: #if entered here means setting a custom color
        windowCascade.Customize.destroy()
        windowCascade.Customize = Customize(windowCascade.root)

def customFontChange(event): #this function will handle the change of custom font to all elements
    global allButtonsFont
    global play_list

    if(allButtonsFont.get() in custom_font_list):
        changeFonts()
        changePlaylistView() #this will reposition elements according to the new font.
        updateSkinMenuLabels()

        if listbox.size() > 0 and play_list.currentSongIndex < listbox.size(): #make playing song visible
            listbox.see(play_list.currentSongIndex)  # Makes sure the given list index is visible. You can use an integer index,
            listbox.selection_clear(0, tk.END)  # clear existing selection
            listbox.select_set(play_list.currentSongIndex)
            listbox.activate(play_list.currentSongIndex)

def updateSkinMenuLabels():
    # this function will update the labels for the Skin Menu from menubar
    if hasattr(menubar, "preferences_skin_menu"):
        for index in range(0, menubar.preferences_skin_menu.index("end")+1):
            menubar.preferences_skin_menu.entryconfigure(index, label=menubar.preferences_skin_menu.entrycget(index, "label").replace(menubar.selectedToken, ""))

        if play_list.skin_theme in skinOptions:
            menubar.preferences_skin_menu.entryconfigure(skinOptions.index(play_list.skin_theme),
                 label=(menubar.selectedToken + play_list.skin_theme.skin_name))
        else:
            menubar.preferences_skin_menu.entryconfigure(menubar.preferences_skin_menu.index("end"),
                 label=(menubar.selectedToken + skinOptions[menubar.preferences_skin_menu.index("end")].skin_name))



def updateViewMenuLabels(): #this function will update the labels for the View Menu from menubar
    if hasattr(menubar, "preferences_view_menu"):
        for index in range(0, menubar.preferences_view_menu.index("end")+1):
            menubar.preferences_view_menu.entryconfigure(index, label=menubar.preferences_view_menu.entrycget(index, "label").replace(menubar.selectedToken, ""))
        if play_list.viewModel == "COMPACT":
            menubar.preferences_view_menu.entryconfigure(0, label=(
                    menubar.selectedToken + menubar.preferences_view_menu.entrycget(0, "label")))
        else:
            menubar.preferences_view_menu.entryconfigure(1, label=(
                    menubar.selectedToken + menubar.preferences_view_menu.entrycget(1, "label")))

def resetSortMenuLabels(): #this function will reset the labels for the Sort Menu from menubar
    if hasattr(menubar, "preferences_sort_menu"):
        for index in range(0, menubar.preferences_sort_menu.index("end")+1):
            menubar.preferences_sort_menu.entryconfigure(index, label=menubar.preferences_sort_menu.entrycget(index, "label").replace(menubar.selectedToken, ""))


def changeSkin(event): #this function will change the skin and readjust the appearance
    global backgroundFile
    global background_label

    if os.path.exists(backgroundFile) and os.path.isfile(backgroundFile):
        background_image = ImageTk.PhotoImage(file=backgroundFile)
        background_label.configure(image=background_image)
        background_label.image = background_image
    else:
        text = ("File: \n\n" + str(backgroundFile) + "\n\ncould not be found.\n" +
                "\n\nThe background image was not loaded.")
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Warning")

    changeFonts() #change the font that comes with the new skin
    changingBackgroundElementColor(event)
    changingBackgroundedLabelsColor()
    changingFontColor(event)
    changingLabelBackgroundColor(event)
    showCurrentSongInList()
    updateSkinMenuLabels()
    updateRadioButtons()
    readjustSearchFormWidth()
    windowCascade.reinitializeOpenedWindows()

def calculateScreenHeightWidth():
    #this function will calculate the Main Window Height and Width needed to properly display the existing content
    #this should be called when changes are done to the appearance
    global allButtonsFont
    mainWindowUpdate() #needed to ensure we calculate the up-to-date width and height
    CurrentFont = allButtonsFont.get()
    fontFam = font.Font(family=CurrentFont.split(" ")[0], size=CurrentFont.split(" ")[1])
    if len(CurrentFont.split(" ")) == 3 and CurrentFont.split(" ")[2] == "bold":
        fontFam = font.Font(family=CurrentFont.split(" ")[0], size=CurrentFont.split(" ")[1], weight=CurrentFont.split(" ")[2])

    screenHeight = fontFam.metrics("linespace")
    screenHeight*=listbox["height"]
    screenHeight+=20 # height of Search Form
    screenHeight+= 100 # the margin on Y axis of the frame.

    frameXPos = getPlayListFramePlacement()

    SearchForm.place(x=frameXPos, y=5)
    ListboxFrame.place(x=frameXPos, y=40)
    screenWidth = frameXPos+ listbox.winfo_reqwidth()+scroll.winfo_reqwidth()+20
    return screenHeight, screenWidth

def getPlayListFramePlacement():
    #this function will determine where is the suitable spot to place the listbox within the player Main Window
    return int(PauseButton.winfo_reqwidth()* 4 ) + int(play_list.buttonSpacing * 3)
    # playlist will be placed in the left side after the buttons

def calculateLetterWidthPixels():
    #this function will calculate the width of character in pixels for the currently used font
    global allButtonsFont
    CurrentFont = allButtonsFont.get()
    fontFam = font.Font(family=CurrentFont.split(" ")[0], size=CurrentFont.split(" ")[1])
    if len(CurrentFont.split(" ")) == 3 and CurrentFont.split(" ")[2] == "bold":
        fontFam ["weight"] = CurrentFont.split(" ")[2]
    return (fontFam.measure("0") + fontFam.measure("A") + fontFam.measure("a"))/3 #compute average width

def seeCompact(): #this function will ensure changing the view to Compact view
    play_list.viewModel = "COMPACT"
    changePlaylistView()

def seePlaylist(): #this function will ensure changing the view to PlayList view
    play_list.viewModel = "PLAYLIST"
    changePlaylistView()

def changePlaylistView(): #this function will change the playlist / player view
    global play_list
    screen_width = windowCascade.root.winfo_screenwidth()
    screen_height = windowCascade.root.winfo_screenheight()
    if play_list.playerXPos > (screen_width-50) or play_list.playerXPos < -50: #in case the last player position was off the screen.
        #50 is a gap. The player will never be out of screen entirely, but it could be invisible, because of start bar/ task bar or other widgets.
        play_list.playerXPos = 0

    if  play_list.playerYPos > (screen_height-50) or play_list.playerYPos < -50: #in case the last player position was off the screen
        #50 is a gap. The player will never be out of screen entirely, but it could be invisible, because of start bar/ task bar or other widgets.
        play_list.playerYPos = 0

    if play_list.viewModel == "COMPACT":
        updateViewMenuLabels()
        windowCascade.root.wm_attributes("-fullscreen", False)
        play_list.playerWidth = PauseButton.winfo_reqwidth()*3 + play_list.buttonSpacing*5 + VolumeScale.winfo_reqwidth()
        play_list.playerHeight = 530
        windowCascade.root.geometry(str(play_list.playerWidth) + "x" + str(play_list.playerHeight) + "+" + str(play_list.playerXPos) + "+" + str(play_list.playerYPos)) #resize and reposition the window
    elif play_list.viewModel == "PLAYLIST":
        updateViewMenuLabels()
        windowCascade.root.wm_attributes("-fullscreen", False)
        listbox["height"] = play_list.listboxNoRows
        play_list.playerHeight, play_list.playerWidth = calculateScreenHeightWidth()  # this will rearrage the buttons under the playlist
        windowCascade.root.geometry(str(play_list.playerWidth) + "x" + str(play_list.playerHeight) + "+" + str(play_list.playerXPos) + "+" + str(play_list.playerYPos)) #resize and reposition the window

def repeat(): #this function is called when clicking on REPEAT button.
    global play_list
    if (play_list.REPEAT==0):
        RepeatButtonText.set("Repeat All")
        play_list.REPEAT = 1
    elif (play_list.REPEAT==1 and play_list.danthologyMode==False):
        RepeatButtonText.set("Repeat One")
        play_list.REPEAT = 2
    elif (play_list.REPEAT==2):
        RepeatButtonText.set("Repeat None")
        play_list.REPEAT = 3
    else:
        if play_list.danthologyMode: #skip Repeat Off is danthology Mode is enabled.
            RepeatButtonText.set("Repeat All")
            play_list.REPEAT = 1
        else:
            RepeatButtonText.set("Repeat Off")
            play_list.REPEAT = 0

def randomize(): #this function will randomize the playlist
    if len(play_list.validFiles) > 0:
        #Changing list to set, the set is automatically randomized, then changing it back again
        random.shuffle(play_list.validFiles)
        # 0-ByFilename ; 1-ByFilenameReversed 2-Randomized; 3-ByRating etc
        play_list.isListOrdered = 2 #2 - is the value for randomized
        updateSortMenuLabel()
        displayElementsOnPlaylist()

def navigationSound(event): #this function is called when clicking on the progressBar
    #this function will readjust the playback position based on the user input
    global play_list
    global progressBarLength
    if len(play_list.validFiles) > 0 and play_list.currentSongIndex!= None:
        x =  (play_list.validFiles[play_list.currentSongIndex].Length / progressBarLength)
        play_list.currentSongPosition = math.floor(event.x * x)

        #if not initialized it means it's not playing
        if pygame.mixer.get_init() == None:
            play_music() #this function will take care of everything and then we can navigate
        pygame.mixer.music.play() #this will restart the song
        pygame.mixer.music.set_pos(play_list.currentSongPosition) #this will set the desired position on the playback
        if play_list.validFiles[play_list.currentSongIndex].fadein_duration > 0 and play_list.currentSongPosition > (play_list.validFiles[play_list.currentSongIndex].startPos +
            play_list.validFiles[play_list.currentSongIndex].fadein_duration):
            if pygame.mixer.music.get_volume() < play_list.VolumeLevel: #in case the user shifted position from beggining when there was fadein enabled.
                pygame.mixer.music.set_volume(play_list.VolumeLevel)
        if play_list.validFiles[play_list.currentSongIndex].fadeout_duration > 0 and play_list.currentSongPosition > (play_list.validFiles[play_list.currentSongIndex].endPos -
            play_list.validFiles[play_list.currentSongIndex].fadeout_duration):
            if pygame.mixer.music.get_volume() < play_list.VolumeLevel: #in case the user shifted position from end when there was fadeout enabled.
                pygame.mixer.music.set_volume(play_list.VolumeLevel)
        progress["value"] = play_list.currentSongPosition
        play_list.RESUMED = True
        if play_list.isSongPause:
            PausedButtonText.set("Pause")
            play_list.isSongPause = False
            SongName.set("Playing: " + play_list.validFiles[play_list.currentSongIndex].fileName)
        if play_list.isSongStopped:
            play_music()

def windSongRight(): #this function will handle the forward of playback for current song
    if len(play_list.validFiles) > 0 and play_list.currentSongIndex!= None:
        play_list.currentSongPosition += 5
        play_list.RESUMED = True

def windSongLeft(): #this function will handle the backward of playback for current song
    if len(play_list.validFiles) > 0 and play_list.currentSongIndex!= None:
        play_list.currentSongPosition -= 5
        play_list.RESUMED = True

def squareBracketsReleased(event):
    #function that gets triggered whenever the square bracket keypresses are released
    #this will handle the playback after the forward / backward maneuvers
    if pygame.mixer.get_init():
        pygame.mixer.music.play()
        pygame.mixer.music.set_pos(play_list.currentSongPosition)

def on_closing(): #this function is called only when the Main Window is canceled/closed
    global APPLICATION_EXIT
    global play_list
    if scheduler.isMainLoopSuspended == True:
        scheduler.userIntervention = True

    APPLICATION_EXIT = True
    # Make a backup of everything:
    if(len(play_list.validFiles) == 0):
        #if empty set these field so that when next song will be added they won't take effect
        play_list.isSongPause = False
        play_list.isSongStopped = False
        play_list.isListOrdered = 0  # 0-ByFilename ; 1-ByFilenameReversed 2-Randomized; 3-ByRating etc
        play_list.currentSongIndex = None
        play_list.currentSongPosition = 0
        play_list.RESUMED = False
    elif pygame.mixer.get_init():
        if play_list.RESUMED: #it means there are songs in the playlist
            play_list.currentSongPosition += math.floor(pygame.mixer.music.get_pos() / 1000)
        else:
            play_list.currentSongPosition = math.floor(pygame.mixer.music.get_pos() / 1000)
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
    #copy window coordinates:
    play_list.playerXPos = windowCascade.root.winfo_x()
    play_list.playerYPos = windowCascade.root.winfo_y()
    #save and close
    file = open(automaticallyBackupFile, "wb")
    pickle.dump(play_list, file)
    file.close()
    windowCascade.root.quit()
    sys.exit()

def remove_song():
    #this function handles the removal of a song within the playlist
    global listBox_Song_selected_index
    if listBox_Song_selected_index!=None:
        if listBox_Song_selected_index < len(play_list.validFiles) and len(play_list.validFiles) > 0:
            #we will impacted the sze of the play_list.validFiles
            if scheduler.isMainLoopSuspended == True:
                #if there are any ongoing loops iterating through play_list.validFiles they need to be stopped
                scheduler.userIntervention = True


            if listBox_Song_selected_index == play_list.currentSongIndex:
                stop_music()
            if play_list.SHUFFLE:
                if listBox_Song_selected_index in play_list.shufflingHistory:
                    play_list.shufflingHistory.remove(listBox_Song_selected_index) #this entry will no longer be valid, since the song was removed.
            play_list.playTime -= play_list.validFiles[listBox_Song_selected_index].Length
            del play_list.validFiles[listBox_Song_selected_index]

            #displayElementsOnPlaylist()
            listbox.delete(listBox_Song_selected_index)
            if listBox_Song_selected_index >= len(play_list.validFiles) and len(play_list.validFiles) > 0:
                listBox_Song_selected_index = len(play_list.validFiles)-1

            if listBox_Song_selected_index < play_list.currentSongIndex:
                #if removing song which is higher up in the playlist then, the currenSongIndex changes
                play_list.currentSongIndex-=1

            if len(play_list.validFiles) > 0:
                textFilesToPlay.set("Files: " + str(len(play_list.validFiles)))
                SongName.set("Paused: " + play_list.validFiles[play_list.currentSongIndex].fileName)
                textTotalPlayTime.set("Total Length: " + formatTimeString(play_list.playTime))
                listbox.selection_clear(0, tk.END)  # clear existing selection
                listbox.see(listBox_Song_selected_index)
                listbox.select_set(listBox_Song_selected_index)
                listbox.activate(listBox_Song_selected_index)
                #listBox_Song_selected_index=None #initialize this if u want to remove only onebyone
            else:
                textFilesToPlay.set("Files: " + str(len(play_list.validFiles)))
                SongName.set("Paused: ")
                textTotalPlayTime.set("Total Length: " + formatTimeString(play_list.playTime))
                g_selected_index = None
                play_list.currentSongIndex = None

def list_selected_item(event):
    #this function gets called when listbox element is selected
    if listbox.size() > 0:
        global listBox_Song_selected_index
        if len(searchValue.get()) == 0:
            listboxSelectedEvent = event.widget
            if (len(listboxSelectedEvent.curselection()) > 0):
                index = int(listboxSelectedEvent.curselection()[0])
                value = listbox.get(index)
                value = value.split(". ")
                listBox_Song_selected_index = int(value[0])
        else:
            listboxSelectedEvent = event.widget
            if(len(listboxSelectedEvent.curselection()) > 0):
                index = int(listboxSelectedEvent.curselection()[0])
                value = listbox.get(index)
                value = value.split(". ")
                listBox_Song_selected_index = int(value[0])
                play_list.currentSongIndex = int(value[0])
                listBox_Song_selected_index = play_list.currentSongIndex

def sortByFileName():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 0
    play_list.validFiles.sort(key=lambda Song: Song.fileName)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByFileNameReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 1
    play_list.validFiles.sort(key=lambda Song: Song.fileName)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortRandomized():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    randomize() #let them be randomized
    #play_list.isListOrdered = 2 # this value is set in function randomize()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    showCurrentSongInList()

def sortByRating():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 3
    play_list.validFiles.sort(key=lambda Song: Song.Rating, reverse=True)  # sort the list according to Rating
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByRatingReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 4
    play_list.validFiles.sort(key=lambda Song: Song.Rating, reverse=True)  # sort the list according to Rating
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByLength():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 5
    play_list.validFiles.sort(key=lambda Song: Song.Length)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByLengthReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 6
    play_list.validFiles.sort(key=lambda Song: Song.Length)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByGenre():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 7
    play_list.validFiles.sort(key=lambda Song: Song.Genre)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByGenreReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 8
    play_list.validFiles.sort(key=lambda Song: Song.Genre)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByNoOfPlays():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 9
    play_list.validFiles.sort(key=lambda Song: Song.NumberOfPlays)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByNoOfPlaysReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 10
    play_list.validFiles.sort(key=lambda Song: Song.NumberOfPlays)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByYear():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 11
    play_list.validFiles.sort(key=lambda Song: Song.Year)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByYearReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 12
    play_list.validFiles.sort(key=lambda Song: Song.Year)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByAlbum():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 13
    play_list.validFiles.sort(key=lambda Song: Song.Album)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByAlbumReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 14
    play_list.validFiles.sort(key=lambda Song: Song.Album)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByTitle():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 15
    play_list.validFiles.sort(key=lambda Song: Song.Title)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByTitleReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 16
    play_list.validFiles.sort(key=lambda Song: Song.Title)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByListenedTime():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 17
    play_list.validFiles.sort(key=lambda Song: Song.SongListenedTime)  # sort the list according to fileName
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByListenedTimeReversed():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 18
    play_list.validFiles.sort(key=lambda Song: Song.SongListenedTime)  # sort the list according to fileName
    play_list.validFiles.reverse()
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByFileMostRecent():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 19
    play_list.validFiles.sort(key=lambda Song: Song.creation_time, reverse=True)  # sort the list according to date the file been modified
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def sortByFileModifiedDate():
    global play_list
    Song = play_list.validFiles[play_list.currentSongIndex]
    play_list.isListOrdered = 20
    play_list.validFiles.sort(key=lambda Song: Song.modified_time)  # sort the list according to date the file been modified
    play_list.currentSongIndex = play_list.validFiles.index(Song)
    displayElementsOnPlaylist()
    updateSortMenuLabel()
    showCurrentSongInList()

def UpdateSongRating():
    #this function will update the song rating when user clicks the radio buttons
    global play_list
    global listBox_Song_selected_index
    if len(play_list.validFiles) > 0 and play_list.currentSongIndex >= 0:
        play_list.validFiles[play_list.currentSongIndex].Rating = int(songRating.get())
        updateRadioButtons()
        if play_list.isListOrdered == 3 or play_list.isListOrdered == 4:
            #if playlist is ordered by rating, update it in real time, since rating has changed
            Song = play_list.validFiles[play_list.currentSongIndex]
            play_list.validFiles.sort(key=lambda Song: Song.Rating, reverse=True)  # sort the list according to Rating
            play_list.currentSongIndex=play_list.validFiles.index(Song)
            displayElementsOnPlaylist()

def updateRadioButtons(): #this function is called when clicking on Song Rating - radio buttons.
    global radioButtonsDefaultColor
    radioButtonsDefaultColor = SkinColor.get()
    color = labelBackground.get()
    if play_list.currentSongIndex != None:
        songRating.set(play_list.validFiles[play_list.currentSongIndex].Rating)
    if play_list.skin_theme.unique_font_color == False:
        radioButtonsDefaultColor = labelBackground.get()
        color = labelTextColor
    if (int(songRating.get()) == 1):
        if labelBackground.get() == SkinColor.get() and play_list.skin_theme.unique_font_color == True:
            # if same sets of colors for buttons and labels we'll invert them in listbox selection to make
            # it look better
            labelSongRating["bg"] = labelBackground.get()
            labelSongRating["fg"] = labelTextColor
            R1["fg"] = labelTextColor
            R1["bg"] = color
        else:
            labelSongRating["bg"] = color
            R1["fg"] = fontColor.get()
            labelSongRating["fg"] = radioButtonsDefaultColor
            R1["bg"] = color
        R2["bg"] = radioButtonsDefaultColor
        R3["bg"] = radioButtonsDefaultColor
        R4["bg"] = radioButtonsDefaultColor
        R5["bg"] = radioButtonsDefaultColor
    elif (int(songRating.get()) == 2):
        if labelBackground.get() == SkinColor.get() and play_list.skin_theme.unique_font_color == True:
            # if same sets of colors for buttons and labels we'll invert them in listbox selection to make
            # it look better
            labelSongRating["bg"] = labelBackground.get()
            labelSongRating["fg"] = labelTextColor
            R1["fg"] = labelTextColor
            R2["fg"] = labelTextColor
            R1["bg"] = color
            R2["bg"] = color
        else:
            labelSongRating["bg"] = color
            labelSongRating["fg"] = radioButtonsDefaultColor
            R1["fg"] = fontColor.get()
            R2["fg"] = fontColor.get()
            R1["bg"] = color
            R2["bg"] = color
        R3["bg"] = radioButtonsDefaultColor
        R4["bg"] = radioButtonsDefaultColor
        R5["bg"] = radioButtonsDefaultColor
    elif (int(songRating.get()) == 3):
        if labelBackground.get() == SkinColor.get() and play_list.skin_theme.unique_font_color == True:
            # if same sets of colors for buttons and labels we'll invert them in listbox selection to make
            # it look better
            labelSongRating["bg"] = labelBackground.get()
            labelSongRating["fg"] = labelTextColor
            R1["fg"] = labelTextColor
            R2["fg"] = labelTextColor
            R3["fg"] = labelTextColor
            R1["bg"] = color
            R2["bg"] = color
            R3["bg"] = color
        else:
            labelSongRating["bg"] = color
            labelSongRating["fg"] = radioButtonsDefaultColor
            R1["fg"] = fontColor.get()
            R2["fg"] = fontColor.get()
            R3["fg"] = fontColor.get()
            R1["bg"] = color
            R2["bg"] = color
            R3["bg"] = color
        R4["bg"] = radioButtonsDefaultColor
        R5["bg"] = radioButtonsDefaultColor
    elif (int(songRating.get()) == 4):
        if labelBackground.get() == SkinColor.get() and play_list.skin_theme.unique_font_color == True:
            # if same sets of colors for buttons and labels we'll invert them in listbox selection to make
            # it look better
            labelSongRating["bg"] = labelBackground.get()
            labelSongRating["fg"] = labelTextColor
            R1["fg"] = labelTextColor
            R2["fg"] = labelTextColor
            R3["fg"] = labelTextColor
            R4["fg"] = labelTextColor
            R1["bg"] = color
            R2["bg"] = color
            R3["bg"] = color
            R4["bg"] = color
        else:
            labelSongRating["bg"] = color
            labelSongRating["fg"] = radioButtonsDefaultColor
            R1["fg"] = fontColor.get()
            R2["fg"] = fontColor.get()
            R3["fg"] = fontColor.get()
            R4["fg"] = fontColor.get()
            R1["bg"] = color
            R2["bg"] = color
            R3["bg"] = color
            R4["bg"] = color
        R5["bg"] = radioButtonsDefaultColor
    elif (int(songRating.get()) == 5):
        if labelBackground.get() == SkinColor.get() and play_list.skin_theme.unique_font_color == True:
            # if same sets of colors for buttons and labels we'll invert them in listbox selection to make
            # it look better
            labelSongRating["bg"] = labelBackground.get()
            labelSongRating["fg"] = labelTextColor
            R1["fg"] = labelTextColor
            R2["fg"] = labelTextColor
            R3["fg"] = labelTextColor
            R4["fg"] = labelTextColor
            R5["fg"] = labelTextColor
            R1["bg"] = color
            R2["bg"] = color
            R3["bg"] = color
            R4["bg"] = color
            R5["bg"] = color
        else:
            labelSongRating["bg"] = color
            labelSongRating["fg"] = radioButtonsDefaultColor
            R1["fg"] = fontColor.get()
            R2["fg"] = fontColor.get()
            R3["fg"] = fontColor.get()
            R4["fg"] = fontColor.get()
            R5["fg"] = fontColor.get()
            R1["bg"] = color
            R2["bg"] = color
            R3["bg"] = color
            R4["bg"] = color
            R5["bg"] = color
    else: #put the default color
        if labelBackground.get() == SkinColor.get() and play_list.skin_theme.unique_font_color == True:
            # if same sets of colors for buttons and labels: we'll invert them in listbox selection to make
            # it look better
            labelSongRating["bg"] = color
            labelSongRating["fg"] = labelTextColor
        else:
            labelSongRating["bg"] = radioButtonsDefaultColor
            labelSongRating["fg"] = color
        R1["bg"] = radioButtonsDefaultColor
        R2["bg"] = radioButtonsDefaultColor
        R3["bg"] = radioButtonsDefaultColor
        R4["bg"] = radioButtonsDefaultColor
        R5["bg"] = radioButtonsDefaultColor
    if len(play_list.validFiles) > 0 and play_list.currentSongIndex!=None:
        songRating.set(str(play_list.validFiles[play_list.currentSongIndex].Rating))

def changingFontColor(event):
    #this function will change font color for all elements except labels
    global play_list
    PauseButton["fg"] = fontColor.get()
    StopButton["fg"] = fontColor.get()
    NextButton["fg"] = fontColor.get()
    PreviousButton["fg"] = fontColor.get()
    ShuffleButton["fg"] = fontColor.get()
    RepeatButton["fg"] = fontColor.get()
    ClearSearchButton["fg"] = fontColor.get()
    labelSearch["fg"] = fontColor.get()

    # changing listbox
    listbox["fg"] = fontColor.get()
    listbox["selectbackground"] = fontColor.get()

    #changing scrollbar style
    scroll_style.configure("Vertical.TScrollbar", arrowcolor=fontColor.get())

    changingBackgroundedLabelsColor()
    showCurrentSongInList()

def changingLabelBackgroundColor(event):
    #this function will change the background color for labels
    global play_list;
    # changing labels
    searchValue["bg"]=labelBackground.get()
    labelPlaying["background"] = labelBackground.get()
    labelPlayingFrame["background"] = labelBackground.get()
    labelProgress["background"] = labelBackground.get()
    labelSize["background"] = labelBackground.get()
    labelFilesToPlay["background"] = labelBackground.get()
    labelLength["background"] = labelBackground.get()
    labelGenre["background"] = labelBackground.get()
    labelStartTime["background"] = labelBackground.get()
    labelEndTime["background"] = labelBackground.get()
    labelTotalPlayTime["background"] = labelBackground.get()
    labelSleepTimer["background"] = labelBackground.get()
    labelWakeTimer["background"] = labelBackground.get()
    labelFadeIn["background"] = labelBackground.get()
    labelFadeOut["background"] = labelBackground.get()
    labelMonoStereoMode["background"] = labelBackground.get()
    labelSampleRate["background"] = labelBackground.get()
    labelNofPlays["background"] = labelBackground.get()
    labelDanthologyMode["background"] = labelBackground.get()
    labelArtist["background"] = labelBackground.get()
    labelAlbum["background"] = labelBackground.get()
    labelTitle["background"] = labelBackground.get()
    labelSongListenedTime["background"] = labelBackground.get()
    labelPlaylistListenedTime["background"] = labelBackground.get()
    labelYear["background"] = labelBackground.get()
    if labelBackground.get() == SkinColor.get() and play_list.skin_theme.unique_font_color == True:
        #if same sets of colors for buttons and labels: we'll invert them in listbox selection to make
        #it look better
        listbox.configure(selectbackground = labelTextColor)
        listbox.configure(selectforeground = labelBackground.get())
        searchValue["bg"] = labelTextColor
        searchValue["fg"] = labelBackground.get()
        scroll_style.configure("Vertical.TScrollbar", bordercolor=labelTextColor)
        progress_style.configure("Horizontal.TProgressbar", background=labelTextColor,
                                 bordercolor=labelTextColor)
        volume_scale_style.configure('Vertical.TScale', background=labelTextColor, troughcolor=labelBackground.get(),
                                     lightcolor=labelTextColor, darkcolor=labelTextColor)
    else:
        listbox.configure(selectbackground=labelBackground.get())
    progress_style.configure("Horizontal.TProgressbar", troughcolor=labelBackground.get())
    scroll_style.configure("Vertical.TScrollbar", troughcolor=labelBackground.get())
    volume_scale_style.configure('Vertical.TScale', troughcolor=labelBackground.get())

def changingBackgroundedLabelsColor():
    #this function will handle changing the font color for labels
    global play_list
    global labelTextColor
    if play_list.skin_theme.unique_font_color == True:
        searchValue["fg"] = fontColor.get()
        labelPlaying["fg"] = fontColor.get()
        labelProgress["fg"] = fontColor.get()
        labelSize["fg"] = fontColor.get()
        labelFilesToPlay["fg"] = fontColor.get()
        labelLength["fg"] = fontColor.get()
        labelGenre["fg"] = fontColor.get()
        labelStartTime["fg"] = fontColor.get()
        labelEndTime["fg"] = fontColor.get()
        labelTotalPlayTime["fg"] = fontColor.get()
        labelSleepTimer["fg"] = fontColor.get()
        labelWakeTimer["fg"] = fontColor.get()
        labelFadeOut["fg"] = fontColor.get()
        labelFadeIn["fg"] = fontColor.get()
        labelMonoStereoMode["fg"] = fontColor.get()
        labelSampleRate["fg"] = fontColor.get()
        labelNofPlays["fg"] = fontColor.get()
        labelDanthologyMode["fg"] = fontColor.get()
        labelArtist["fg"] = fontColor.get()
        labelAlbum["fg"] = fontColor.get()
        labelTitle["fg"] = fontColor.get()
        labelSongListenedTime["fg"] = fontColor.get()
        labelPlaylistListenedTime["fg"] = fontColor.get()
        labelYear["fg"] = fontColor.get()
        labelTextColor = fontColor.get()
        if labelBackground.get() == SkinColor.get() and play_list.skin_theme.unique_font_color == True:
            # if same sets of colors for buttons and labels: we'll invert them in listbox selection to make
            # it look better
            listbox.configure(selectbackground=labelTextColor)
            listbox.configure(selectforeground=labelBackground.get())
            searchValue["bg"] = labelTextColor
            searchValue["fg"] = labelBackground.get()
            scroll_style.configure("Vertical.TScrollbar", bordercolor=labelTextColor)
            progress_style.configure("Horizontal.TProgressbar", background=labelTextColor,
                                     bordercolor=labelTextColor)
            volume_scale_style.configure('Vertical.TScale', background=labelTextColor,
                                         troughcolor=labelBackground.get(),
                                         lightcolor=labelTextColor, darkcolor=labelTextColor)
        else:
            listbox.configure(selectforeground=fontColor.get())
    else:
        color = PauseButton["bg"] #put the same color as button background
        searchValue["fg"] = color
        labelPlaying["fg"] = color
        labelProgress["fg"] = color
        labelSize["fg"] = color
        labelFilesToPlay["fg"] = color
        labelLength["fg"] = color
        labelGenre["fg"] = color
        labelStartTime["fg"] = color
        labelEndTime["fg"] = color
        labelTotalPlayTime["fg"] = color
        labelSleepTimer["fg"] = color
        labelWakeTimer["fg"] = color
        labelFadeOut["fg"] = color
        labelFadeIn["fg"] = color
        labelMonoStereoMode["fg"] = color
        labelSampleRate["fg"] = color
        labelNofPlays["fg"] = color
        labelDanthologyMode["fg"] = color
        labelArtist["fg"] = color
        labelAlbum["fg"] = color
        labelTitle["fg"] = color
        labelSongListenedTime["fg"] = color
        labelPlaylistListenedTime["fg"] = color
        labelYear["fg"] = color
        labelTextColor = color
        listbox.configure(selectforeground=color)
        scroll_style.configure("Vertical.TScrollbar", arrowcolor=fontColor.get())

def move_up(): #this function will move the selected song up in the playlist
    global listBox_Song_selected_index
    if listBox_Song_selected_index != None:
        Song = play_list.validFiles[listBox_Song_selected_index] #this is the auxiliar variable
        if(listBox_Song_selected_index-1 >= 0):
            #interchanging values
            play_list.validFiles[listBox_Song_selected_index] = play_list.validFiles[listBox_Song_selected_index-1]
            play_list.validFiles[listBox_Song_selected_index - 1] = Song

            listbox.delete(listBox_Song_selected_index)
            listbox.insert(listBox_Song_selected_index-1,
                           str(listBox_Song_selected_index-1) + ". " + play_list.validFiles[listBox_Song_selected_index-1].fileName)

            listbox.delete(listBox_Song_selected_index)
            listbox.insert(listBox_Song_selected_index,
                           str(listBox_Song_selected_index) + ". " + play_list.validFiles[listBox_Song_selected_index].fileName)

            listBox_Song_selected_index -=1

            listbox.selection_clear(0, tk.END)  # clear existing selection
            listbox.see(listBox_Song_selected_index)
            listbox.select_set(listBox_Song_selected_index)
            listbox.activate(listBox_Song_selected_index)

            # listBox_Song_selected_index=None #initialize this if u want to move only onebyone
            play_list.isListOrdered = 21 #this will mean Custom Sorting
            updateSortMenuLabel()

def move_down(): #this function is will move the selected song down in the playlist
    global listBox_Song_selected_index
    if listBox_Song_selected_index != None:
        Song = play_list.validFiles[listBox_Song_selected_index]  # this is the auxiliar variable
        if (listBox_Song_selected_index + 1 < len(play_list.validFiles)):
            # interchanging values
            play_list.validFiles[listBox_Song_selected_index] = play_list.validFiles[listBox_Song_selected_index + 1]
            play_list.validFiles[listBox_Song_selected_index + 1] = Song

            listbox.delete(listBox_Song_selected_index)
            listbox.insert(listBox_Song_selected_index,
                           str(listBox_Song_selected_index) + ". " + play_list.validFiles[listBox_Song_selected_index].fileName)

            listbox.delete(listBox_Song_selected_index+1)
            listbox.insert(listBox_Song_selected_index+1,
                           str(listBox_Song_selected_index+1) + ". " + play_list.validFiles[listBox_Song_selected_index+1].fileName)

            listBox_Song_selected_index += 1

        listbox.selection_clear(0, tk.END)  # clear existing selection
        listbox.see(listBox_Song_selected_index)
        listbox.select_set(listBox_Song_selected_index)
        listbox.activate(listBox_Song_selected_index)
        # listBox_Song_selected_index=None #initialize this if u want to move only onebyone
        play_list.isListOrdered = 21 #this will mean Custom Sorting
        updateSortMenuLabel()

def changeFonts():
    PauseButton["font"] = allButtonsFont.get()
    StopButton["font"] = allButtonsFont.get()
    NextButton["font"] = allButtonsFont.get()
    PreviousButton["font"] = allButtonsFont.get()
    ShuffleButton["font"] = allButtonsFont.get()
    RepeatButton["font"] = allButtonsFont.get()
    ClearSearchButton["font"] = allButtonsFont.get()
    # changing labels
    labelPlaying["font"] = allButtonsFont.get()
    labelProgress["font"] = allButtonsFont.get()
    labelSize["font"] = allButtonsFont.get()
    labelFilesToPlay["font"] = allButtonsFont.get()
    labelLength["font"] = allButtonsFont.get()
    labelGenre["font"] = allButtonsFont.get()
    labelStartTime["font"] = allButtonsFont.get()
    labelEndTime["font"] = allButtonsFont.get()
    labelTotalPlayTime["font"] = allButtonsFont.get()
    labelSleepTimer["font"] = allButtonsFont.get()
    labelWakeTimer["font"] = allButtonsFont.get()
    labelFadeOut["font"] = allButtonsFont.get()
    labelFadeIn["font"] = allButtonsFont.get()
    labelMonoStereoMode["font"] = allButtonsFont.get()
    labelSampleRate["font"] = allButtonsFont.get()
    labelNofPlays["font"] = allButtonsFont.get()
    labelDanthologyMode["font"] = allButtonsFont.get()
    labelArtist["font"] = allButtonsFont.get()
    labelAlbum["font"] = allButtonsFont.get()
    labelTitle["font"] = allButtonsFont.get()
    labelSongListenedTime["font"] = allButtonsFont.get()
    labelPlaylistListenedTime["font"] = allButtonsFont.get()
    labelYear["font"] = allButtonsFont.get()
    labelSearch["font"] = allButtonsFont.get()
    # changing listbox
    listbox["font"] = allButtonsFont.get()
    searchValue["font"] = allButtonsFont.get()
    #changing radiobuttons:
    R1["font"] = allButtonsFont.get()
    R2["font"] = allButtonsFont.get()
    R3["font"] = allButtonsFont.get()
    R4["font"] = allButtonsFont.get()
    R5["font"] = allButtonsFont.get()
    labelSongRating["font"] = allButtonsFont.get()
    buttonAdjustments()
    reSpacePositionElements()  # respace elements

def packPositionButton(): #function called only at the startup to place the buttons for COMPACT view
    # column1:
    global play_list
    horizontalButtonsColumnStartCoord = 5

    PreviousButton.place(x=horizontalButtonsColumnStartCoord, y=5)
    RepeatButton.place(x=horizontalButtonsColumnStartCoord, y=37)

    # column2:
    horizontalButtonsColumnStartCoord += PauseButton.winfo_reqwidth() + play_list.buttonSpacing
    StopButton.place(x=horizontalButtonsColumnStartCoord, y=37)
    PauseButton.place(x=horizontalButtonsColumnStartCoord, y=5)

    # column3:
    horizontalButtonsColumnStartCoord += PauseButton.winfo_reqwidth() + play_list.buttonSpacing
    NextButton.place(x=horizontalButtonsColumnStartCoord, y=5)
    ShuffleButton.place(x=horizontalButtonsColumnStartCoord, y=37)

    #column 4
    horizontalButtonsColumnStartCoord += PauseButton.winfo_reqwidth() + play_list.buttonSpacing
    VolumeScale.place(x = horizontalButtonsColumnStartCoord, y=5)

def reSpacePositionElements():
    #function called when changing skin, fonts or appearance to reposition the elements
    # (buttons, listbox, labels, progressbar)
    global progressBarLength

    column_start = 5
    column_start += PauseButton.winfo_reqwidth() + play_list.buttonSpacing

    # column2
    PauseButton.place(x=column_start, y=5)
    StopButton.place(x=column_start, y=37)

    column_start += PauseButton.winfo_reqwidth() + play_list.buttonSpacing

    # column3:
    NextButton.place(x= column_start, y=5) # - 4 because border uses 2px on each side of the button
    ShuffleButton.place(x=column_start, y=37) # - 4 because border uses 2px on each side of the button

    column_start += PauseButton.winfo_reqwidth() + play_list.buttonSpacing

    #column 4
    VolumeScale.place(x=column_start , y=5)
    VolumeScale["length"] = (PauseButton.winfo_reqheight()*2) #volume_scale length is based on button column height

    #progressbar
    progressBarLength = column_start - progressBarMargin
    progress["length"] = progressBarLength

    # playing label
    labelPlaying["wraplength"] = progressBarLength - 4 # - 4 becuase of the borders
    labelPlaying["width"] = int(progressBarLength / calculateLetterWidthPixels())-2
    labelPlayingFrame["width"] = progressBarLength

    # column 2 for following labels

    #column_start is calculated based on the longest label from column 1
    #which currently is either labelSampleRate or labelDanthologyMode
    column_start = labelSampleRate.winfo_reqwidth() + (play_list.buttonSpacing * 2) + 10 #10 is the margin for labels
    if labelSampleRate.winfo_reqwidth() < labelDanthologyMode.winfo_reqwidth():
        column_start = labelDanthologyMode.winfo_reqwidth() + (play_list.buttonSpacing * 3)
    #considering labelSongListenedTime the longest label in the first column

    # column 2
    labelProgress.place(x=column_start, y=170)
    labelLength.place(x=column_start, y=190)
    labelGenre.place(x=column_start, y=210)
    labelSongListenedTime.place(x=column_start, y=230)
    labelStartTime.place(x=column_start, y=250)
    labelEndTime.place(x=column_start, y=270)
    labelSleepTimer.place(x=column_start, y=290)
    labelWakeTimer.place(x=column_start, y=310)

    changePlaylistView()

def packPositionLabels(): #function called only at the start, to position the labels.
    #under progressBar:
    labelPlaying.place(x=0, y=0)
    labelPlayingFrame.place(x=10, y=100)

    # Placing the labels

    #column 1
    labelMonoStereoMode.place(x=10, y=170)
    labelFadeIn.place(x=10, y=190)
    labelFadeOut.place(x=10, y=210)
    labelSampleRate.place(x=10, y=230)
    labelDanthologyMode.place(x=10, y=250)
    labelFilesToPlay.place(x=10, y=270)
    labelNofPlays.place(x=10, y=290)
    labelSize.place(x=10, y=310)

    # column 2
    labelProgress.place(x=180, y=170)
    labelLength.place(x=180, y=190)
    labelGenre.place(x=180, y=210)
    labelSongListenedTime.place(x=180, y=230)
    labelStartTime.place(x=180, y=250)
    labelEndTime.place(x=180, y=270)
    labelSleepTimer.place(x=180, y=290)
    labelWakeTimer.place(x=180, y=310)

    labelTotalPlayTime.place(x=10, y=340)
    labelPlaylistListenedTime.place(x=10, y=360)

    #Bottom labels
    labelArtist.place(x=10, y=420)
    labelYear.place(x=10, y=440)
    labelTitle.place(x=10, y=460)
    labelAlbum.place(x=10, y=480)

def pressedCtrlRight(event): #this function will reset the Current track when CTRL_RIGHT is pressed
    resetTrack()

def resetTrack(): #this function will reset the Current track
    play_list.currentSongPosition = 0
    play_music()

def pressedEnter(event):
    #this function will play next_song when ENTER is pressed
    if pygame.mixer.get_init():
        if pygame.mixer.music.get_busy():
            next_song()
        else:
            showCurrentSongInList()
            play_music()
    else:
        showCurrentSongInList()
        play_music()

def pressedShiftRight(event):
    #this function will play previous_song when SHIFT_RIGHT is pressed
    if pygame.mixer.get_init():
        if pygame.mixer.music.get_busy():
            previous_song()
        else:
            play_music()
    else:
        play_music()

def pressedShiftLeft(event):
    # function that will be called on specific key press is pressed and will move the selected song
    move_up()

def pressedCtrlLeft(event):
    # function that will be called on specific key press is pressed and will move the selected song
    move_down()

def pressedDelete(event):
    #function that will be called when Delete key is pressed and will remove the selected song
    remove_song()

def mutePlayback():
    #function that will mute the playback volume
    if pygame.mixer.get_init():
        if pygame.mixer.music.get_volume() > 0:
            pygame.mixer.music.set_volume(0)
            VolumeScale.set(0.0)
        else:
            pygame.mixer.music.set_volume(play_list.VolumeLevel)
            VolumeScale.set(play_list.VolumeLevel * 100)

def pressedKeyShortcut(event):
    #function that handles key presses and triggers proper actions
    if windowCascade.root.focus_get() != searchValue:
        if event.char == " ":
            pause_music()
        elif event.char == "m" or event.char == "M":
            mutePlayback()
        elif event.char == ".":
            volume_up()
        elif event.char == ",":
            volume_down()
        elif event.char == "r" or event.char == "R":
            repeat()
        elif event.char =="s" or event.char =="S":
            shuffle()
        elif event.char =="d" or event.char =="D":
            stop_music()
        elif event.char == "1":
            play_list.VolumeLevel = 0.1
            VolumeScale.set(play_list.VolumeLevel * 100)
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(play_list.VolumeLevel)
        elif event.char == "2":
            play_list.VolumeLevel = 0.2
            VolumeScale.set(play_list.VolumeLevel * 100)
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(play_list.VolumeLevel)
        elif event.char == "3":
            play_list.VolumeLevel = 0.3
            VolumeScale.set(play_list.VolumeLevel * 100)
            VolumeScale.set(play_list.VolumeLevel * 100)
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(play_list.VolumeLevel)
        elif event.char == "4":
            play_list.VolumeLevel = 0.4
            VolumeScale.set(play_list.VolumeLevel * 100)
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(play_list.VolumeLevel)
        elif event.char == "5":
            play_list.VolumeLevel = 0.5
            VolumeScale.set(play_list.VolumeLevel * 100)
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(play_list.VolumeLevel)
        elif event.char == "6":
            play_list.VolumeLevel = 0.6
            VolumeScale.set(play_list.VolumeLevel * 100)
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(play_list.VolumeLevel)
        elif event.char == "7":
            play_list.VolumeLevel = 0.7
            VolumeScale.set(play_list.VolumeLevel * 100)
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(play_list.VolumeLevel)
        elif event.char == "8":
            play_list.VolumeLevel = 0.8
            VolumeScale.set(play_list.VolumeLevel * 100)
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(play_list.VolumeLevel)
        elif event.char == "9":
            VolumeScale.set(play_list.VolumeLevel * 100)
            play_list.VolumeLevel = 0.9
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(play_list.VolumeLevel)
        elif event.char == "0":
            VolumeScale.set(play_list.VolumeLevel * 100)
            play_list.VolumeLevel = 1.0
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(play_list.VolumeLevel)
                VolumeScale.set(play_list.VolumeLevel * 100)
        elif event.char == "a" or event.char == "A":
            showSlideshow()
        elif event.char == "p" or event.char == "P":
            showCustomizeWindow()
        elif event.char == "i" or event.char == "I":
            showKeybordShortcuts()
        elif event.char == "q" or event.char == "Q":
            showCuttingTool()
        elif event.char == "t" or event.char == "T":
            showSleepingTool()
        elif event.char == "h" or event.char == "H":
            showMp3TagModifierWindow()
        elif event.char == "l" or event.char == "L":
            showGrabLyricsWindow()
        elif event.char == "g" or event.char == "G":
            showArtistBioWindow()
        elif event.char == "]":
            windSongRight() #this will move song progress to the right
        elif event.char == "[":
            windSongLeft() #this will move song progress to the left

def showKeybordShortcuts():
    #function that displays in separate window all available hotkeys and keyboard shortcuts
    text = ("List of all the shortcut keys: \n\n"
        + "LEGEND:\n\n"
        + "Keyboard Shortcuts trigger events only when the PyPlay Window is focused.\n"
        + "Hotkeys are keyboard shortcuts that trigger event also when the window is not focused or minimized:\n\n"
        + "HOTKEYS FOR MEDIA CONTROL:\n\n"
        + "Media Play/Pause - hotkey used to toggle Play/Pause.\n"
        + "Media Next - hotkey used to jump to the Next Song.\n"
        + "Media Previous - hotkey used to jump to the Previous Song.\n\n"
        + "KEYBOARD SHORTCUTS:\n\n"
        + "For Playback Control:\n"
        + "S - is used to trigger the Shuffle Button.\n"
        + "D - is used to trigger the Stop Button.\n"
        + "R - is used to trigger the Repeat Button.\n"
        + "SHIFT_R - is used to trigger the Previous Button.\n"
        + "ENTER - is used to trigger the Next Button.\n"
        + "CTRL_R - is used to trigger the Reset Track Command.\n"
        + "SPACE - is used to Play/Pause, or to hit the focused button selected using Tab.\n"
        + "M - is used to Mute the playback volume.\n"
        + "[1-9] - is used to change the Playback Volume from 10% - 90%\n"
        + "[0] -is used to change the Playback Volume to 100%\n"
        + ". or > key - is equivalent to Volume Up.\n"
        + ", or < key - is equivalent to Volume Down.\n"
        + "[ ] - will rewing Forwards or Backwards the playback Progress.\n\n"
        + "For Other Player Functions:\n"
        + "Q - opens the Cutting Tool Window\n"
        + "T - opens the Sleeping Tool Window\n"
        + "L - is used to Search Song Lyrics Online\n"
        + "G - is used to Search Artist Biography Online\n"
        + "P - opens the Customize Window\n"
        + "A - opens the Slideshow Window\n"
        + "TAB - slides between the opened Windows, or player elements.\n"
        + "L_SHIFT - is used to Move Up on the current playlist song selection.\n"
        + "L_CTRL - is used to Move Down on the current playlist song selection.\n"
        + "Delete - is used to Remove on the current playlist song selection.\n"
        + "Page Up or Up - can be used to navigate the playlist UP.\n"
        + "Page Down or Down - can be used to navigate the playlist DOWN.\n"
        + "I - will show this message again.")
    WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Keyboard Shortcuts")

def listboxShortcuts(event):
    #function that handles the listbox keyboard shortcuts
    if event.char == "w":
        if windowCascade.Mp3TagModifierTool == None:
            if listBox_Song_selected_index!=None and len(searchValue.get()) == 0:
                Mp3TagModifierTool(listBox_Song_selected_index)
                windowCascade.Mp3TagModifierTool.ComposeNameCheckButtonVar.set(1)
                windowCascade.Mp3TagModifierTool.checkUncheckNameComposal(event)
                windowCascade.Mp3TagModifierTool.SaveChanges()
                windowCascade.Mp3TagModifierTool.destroy()
        else:
            text = "Window is already opened."
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

def songInfo():
    #function that displays in a separate window the song Info stored in the player
    element = play_list.validFiles[listBox_Song_selected_index]
    mode = "Stereo" if element.channels == 2 else "Mono"

    textLabel = "Info About File: \n\n" \
    + "Filename: " + str(element.fileName) + "\n" \
    + "Path: " + str(element.filePath) + "\n" \
    + "Size: " + str(element.fileSize) + " MB\n" \
    + "Creation Date: " + str(time.ctime(element.creation_time)) + "\n" \
    + "Modified Date: " + str(time.ctime(element.modified_time)) + "\n" \
    + "Bit Rate: " + str(element.bitrate) + "\n" \
    + "Sample Rate: " + str(element.sample_rate) + "\n" \
    + "Mode: " + str(mode) + "\n" \
    +"\nFile Tags:\n\n" \
    + "Album: " + str(element.Album) + "\n" \
    + "Year: " + str(element.Year) + "\n" \
    + "Genre: " + str(element.Genre) + "\n" \
    + "Artist: " + str(element.Artist) + "\n" \
    + "Title: " + str(element.Title) + "\n" \
    + "Length: " + formatTimeString(element.Length) + "\n" \
    + "\nInternal Player Settings:\n\n" \
    + "Rating: " + str(element.Rating) + "\n" \
    + "FadeIn: " + str(element.fadein_duration) + "\n" \
    + "FadeOut: " + str(element.fadeout_duration) + "\n" \
    + "Start Time: " + formatTimeString(element.startPos) + "\n" \
    + "End Time: " + formatTimeString(int(element.endPos)) + "\n" \
    + "Number Of Plays: " + str(element.NumberOfPlays) + "\n" \
    + "Song Listening Time: " + str(formatTimeString(element.SongListenedTime)) + "\n"
    WindowDialog(textLabel, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Song Info")

def openFileInExplorer():
    #function that opens the selected file in windows explorer
    file = play_list.validFiles[listBox_Song_selected_index].filePath
    FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
    subprocess.Popen([FILEBROWSER_PATH, '/select,', os.path.normpath(file)])

def resynchronizeFile(index):
    #function that resynchronizes / re-imports the relevant data from the drive
    #for specified song within the playlist
    play_list.validFiles[index].refreshSongData()
    if play_list.validFiles[index].Exception != None:
        text = "File: \n" + str(play_list.validFiles[index].filePath) + "\n" + \
                "Reason: " + str(play_list.validFiles[index].Exception) + "\n\n"
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("Do Nothing", None),
                     Button2_Functionality=ButtonFunctionality("Remove Invalid File", removeInvalidFiles([play_list.validFiles[index]])),
                     windowTitle="Resynchronize Log")

def rightClickListboxElement(event):
    #function that displays the context menu on right-click within the listbox
    if listBox_Song_selected_index != None:
        listboxSelectedEvent = event.widget
        if len(listboxSelectedEvent.curselection()) > 0:
            index = 0
            if len(searchValue.get()) == 0:
                index = int(listboxSelectedEvent.curselection()[0])
            else:
                index = int(listboxSelectedEvent.curselection()[0])
                value = listbox.get(index)
                value = value.split(". ")
                index = int(value[0])
            aMenu = tk.Menu(windowCascade.root, tearoff=0)
            aMenu.add_command(label='Randomize List', command=sortRandomized)
            aMenu.add_command(label='Delete From List', command=remove_song)
            aMenu.add_command(label='File Info', command=songInfo)
            aMenu.add_command(label='Resynchronize File', command=lambda: resynchronizeFile(index))
            aMenu.add_command(label='Move Up', command=move_up)
            aMenu.add_command(label='Move Down', command=move_down)
            aMenu.add_command(label='Open File in Explorer', command=openFileInExplorer)
            aMenu.add_command(label='Show Current Track', command=showCurrentSongInList)
            aMenu.add_command(label='MP3 Tag Modifier Tool', command= lambda:showMp3TagModifierWindow(index))
            aMenu.add_command(label='Search Song Lyrics Online', command= lambda:showGrabLyricsWindow(index))
            aMenu.add_command(label='Read Artist Biography', command= lambda:showArtistBioWindow(index))
            aMenu.add_command(label='Cut Playback Length', command= lambda:showCuttingTool(index))
            aMenu.post(event.x_root, event.y_root)

def showCurrentSongInList():
    #function that will refresh selection in the listbox ensuring the song loaded in the playback is selected/highlighted
    global listBox_Song_selected_index
    if play_list.currentSongIndex != None:
        if listbox.size() > 0 and play_list.currentSongIndex < listbox.size(): #make playing song visible
            listBox_Song_selected_index = play_list.currentSongIndex
            firstVisibleElementInList = listbox.nearest(0)
            lastVisibleElementInList = listbox.nearest(0) + listbox["height"] - 1
            listbox.selection_clear(0, tk.END)  # clear existing selection
            listbox.select_set(listBox_Song_selected_index)
            listbox.activate(listBox_Song_selected_index)
            # If the element playing is not visible in the listbox:
            if listBox_Song_selected_index < firstVisibleElementInList or listBox_Song_selected_index > lastVisibleElementInList:
                listbox.see(listBox_Song_selected_index)

def showSlideshow():
    if windowCascade.Slideshow == None:
        Slideshow()
    else:
        text = "Slideshow Window is already opened."
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle="Information")

def showMp3TagModifierWindow(index=None):
    if index == None and listBox_Song_selected_index == None:
        text = "Playback is empty or no file was selected."
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
    else:
        if index == None and listBox_Song_selected_index != None:
            index = listBox_Song_selected_index
        if index != None:
            if windowCascade.Mp3TagModifierTool == None:
                Mp3TagModifierTool(index)
            else:
                text = "MP3 Tag Modifier Window is already opened."
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

def showAboutWindow():
    text = ("Current Version: V4\n\n" + \
            "PyPlay MP3 Player is an application which was developed as challenge \n" +
            "in order to improve knowledge, coding skills and understanding of \n" +
            "Python: high-level programming & scripting language \n\n" +

            "The application is available as following: \n" +

            "For Windows: a compiled version is available containing the executable file \n" +
            "with all the resources required to run.\n\n"+

            "Portable Script: a python pre-installed version is available. This version \n"  +
            "contains the Python Script File (source code) and Python 3.10 with all the \n"+
            "development libraries required to run the script.\n\n" +
            
            "Versions deployed: \n"
            "PyPlay Mp3 Player V3 \n"
            "PyPlay Mp3 Player V4 \n\n"
            
            "PyPlay Mp3 Player V3 designed in 2019 developed using Python 3.4.\n"
            "PyPlay Mp3 Player V4 improved version in 2025 updated to Python 3.10.\n\n"
            
            "For Windows: Compiled versions are available containing the executable file with all the resources required to run. \n"
            "For PyPlay Mp3 Player V3 the compilation was done using: Py2Exe.\n"
            "For PyPlay Mp3 Player V4 the compilation was done using: PyInstaller.\n\n"
            
            "Portability: The runnable scripts archives contain pre-installed version of Python used in the development. "
            "The archives contain the .py python script files (source code) all resources required to run the script python.\n\n"
            
            "What can V3 script do:\n\n"
            
            "- playing .mp3 files,\n"
            "- create and manage .mp3 file playlists.\n"
            "- customizable player's appearance.\n"
            "- rename and edit .mp3 file tags in Real-Time (without stopping the playback).\n"
            "- adjust the playback length for the files within the playlist.\n"
            "- add track independently fading in and fading out effects.\n"
            "- rating system for the tracks within a playlist.\n"
            "- Sleep and Wake Up timers.\n"
            "- real-time web-crawling for Track Lyrics.\n"
            "- real-time web-crawling for Artist Biographies.\n"
            "- attach Slideshows.\n"
            "- adds Cross-Fading for Track Transitions.\n"
            "- Shuffling without repeats.\n"
            "- sets automatic track switching time-intervals (Danthology Mode).\n"
            "- tracking of the number of times each track was played.\n"
            "- auto-filling of the missing MP3 Tag Information such us: Artist, Name, Album, Year directly from the Web.\n"
            "- auto-text editing / renaming files taking as reference MP3 Tags.\n"
            "- various sorting methods available.\n"
            "- real-time search capability within playlists.\n"
            "- playlists Stats tracking.\n"
            "- able to generate Excel reports for Playlist & Track Statistics;\n"
            "- string filtering and processing of file names. Able to remove unwanted characters"
            "in real-time for every file in the playlist;\n\n"
            
            "What changed in V4:\n"
            "- added menu bar on main window\n"
            "- added search form on main window\n"
            "- improved instant search\n"
            "- added hotkeys for remote support of Play/Pause and Next/Previous track through use of Media"
            "Play/Pause, Media Next, Media Previous button available from keyboard or wireless headsets.\n"
            "- added support for associating PyPlay with .mp3 files.\n"
            "- added more fonts\n"
            "- added better styles for scrollbar, volume scale, progress bar\n"
            "- improved performance regarding window responsiveness\n"
            "- added resynchronize context menu command to validate / refresh / update  .mp3 "
            "file data from drive into the player\n"
            "- added flagging mechanism to monitor/determine the corruption of files within the playlist\n"
            "- reduce the number of views available for the Player\n"
            "- restructuring of resources and backup files\n"
            "- amount of button elements was reduces\n"
            "- new skin themes added\n"
            "- fixed bugs regarding the Slideshow\n"
            "- support for opening more than 2 windows at once\n"
            "- added projections for the Mass File Editor options for handling multiple files within Mp3 Tag Modifier Tool\n"
            "- limits the application instances to 1. The user can only open 1 instance of the player." )

    WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "About")

def showCustomizeWindow():
    if windowCascade.Customize == None:
        Customize(windowCascade.root)
    else:
        text = "Customize Window is already opened."
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

def showGrabLyricsWindow(index="empty"):
    if windowCascade.GrabLyricsTool == None:
        GrabLyricsTool(index)
    else:
        text = "GrabLyrics Window is already opened."
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

def showArtistBioWindow(index="empty"):
    if windowCascade.GrabArtistBio == None:
        GrabArtistBio(index)
    else:
        text = "ArtistBio Window is already opened."
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

def showSlideshowWindow():
    if windowCascade.Slideshow == None:
        Slideshow()
    else:
        text = "Slideshow is already opened."
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

def checkResynchronizePlaylist():
    # function that checks for updates regarding the playlist. Checks if new files can be imported from
    # the playlist directories or if existing files are still valid

    text = ""
    invalidFiles = []
    newFiles = []

    scheduler.suspend_mainloop()
    for element in play_list.validFiles:
        if scheduler.userIntervention == True:
            # user changed something in the play_list that might affect the outcome of this loop
            scheduler.userIntervention = False
            break
        scheduler.single_loop() # this will make the main window responsive
        element.refreshSongData()
        windowCascade.root.title("Resynchronizing file: " + element.fileName)
        if element.Exception != None:
            invalidFiles.append(element)
            text += "File: \n" + str(element.filePath) + "\n" + "Reason: " + str(element.Exception) + "\n\n"

    scheduler.resume_mainloop()

    message = ""
    added_playTime = 0
    message, newFiles, added_playTime = scanForNewFilesInDirectories(play_list.dirFilePath)

    text += message

    windowCascade.root.title(Project_Title)
    if text!="":
        text = "Change Log: \n\n" + text
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("Update Playlist",
                                   lambda: commitUpdatesToPlaylist(invalidFiles, newFiles, added_playTime)),
                     windowTitle="Resynchronize Log")
    else:
        text = "No new changes."
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None),
                     windowTitle="Information")

def commitUpdatesToPlaylist(invalidFiles: list, newFiles: list, added_playTime: int):
    #function to resynchronize the playlist
    removeInvalidFiles(invalidFiles)
    play_list.validFiles += newFiles
    displayElementsOnPlaylist()
    showCurrentSongInList()
    updateSortMenuLabel()
    play_list.isListOrdered = 21  # this will mean Custom Sorting
    textFilesToPlay.set("Files: " + str(len(play_list.validFiles)))
    play_list.playTime += added_playTime
    textTotalPlayTime.set("Total Length: " + formatTimeString(play_list.playTime))

def removeInvalidFiles(invalidFiles: list):
    #function that will remove invalid files from the playlist after resynchronizing
    scheduler.suspend_mainloop()
    for element in invalidFiles:
        windowCascade.root.title("Removing from playlist: " + element.fileName)
        if element in play_list.validFiles:
            del play_list.validFiles[play_list.validFiles.index(element)]
        scheduler.single_loop()  # this will make the main window responsive

    scheduler.resume_mainloop()
    displayElementsOnPlaylist()
    windowCascade.root.title(Project_Title)

def showFlaggedMp3Files():
    messageForUser = ""
    scheduler.suspend_mainloop()
    for element in play_list.validFiles:
        if scheduler.userIntervention == True:
            # user changed something in the play_list that might affect the outcome of this loop
            scheduler.userIntervention = False
            break
        element.refreshSongData()
        windowCascade.root.title("Scanning for Flagged Files: " + element.fileName)
        if element.Exception != None:
            messageForUser += "File: " + element.filePath + "\nReason: " + str(element.Exception) + "\n\n"
        scheduler.single_loop()  # this will make the main window responsive

    scheduler.resume_mainloop()
    text = "No flagged mp3 files. All the files within the Playlist are playable."
    if messageForUser != "":
        text = "The following .mp3 files were flagged by the player. Check out the reasons below: \n\n" + messageForUser
    WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle="Flagged Files")
    windowCascade.root.title(Project_Title)

def rightClickOnWindow(event):
    #function that displays the context menu on right-click within the window
    if windowCascade.root.winfo_containing(event.x_root, event.y_root) != listbox: # don't execute this if the cursor is inside the listbox
        aMenu = tk.Menu(windowCascade.root, tearoff=0)
        aMenu.add_command(label='About', command=showAboutWindow)
        aMenu.add_command(label='Customize', command=showCustomizeWindow)
        aMenu.add_command(label='Slideshow', command=showSlideshowWindow)
        aMenu.add_command(label='Sleeping Tool', command=showSleepingTool)
        aMenu.add_command(label='Cutting Tool', command=showCuttingTool)
        aMenu.add_command(label='MP3 Tag Modifier Tool', command=showMp3TagModifierWindow)
        aMenu.add_command(label='Search Song Lyrics Online', command=showGrabLyricsWindow)
        aMenu.add_command(label='Read Artist Biography', command=showArtistBioWindow)
        aMenu.add_command(label='Playlist Info', command=showPlaylistInfo)
        aMenu.add_command(label='Open PyPlay Directory', command=openPyPlayDirectory)
        aMenu.add_command(label='Resynchronize Playlist', command=checkResynchronizePlaylist)
        aMenu.add_command(label='Flagged Files Status', command=showFlaggedMp3Files)
        aMenu.add_command(label='Cancel Current Operation', command=cancelOperation)
        aMenu.post(event.x_root, event.y_root)

def cancelOperation():
    #this function will set the userIntervention flag which will break out of ongoing loops
    global scheduler
    if scheduler.isMainLoopSuspended == True:
        scheduler.userIntervention = True

def openPyPlayDirectory():
    #function that opens the application root directory
    FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
    subprocess.Popen([FILEBROWSER_PATH, '/select,', os.path.normpath(sys.argv[0])])

def calculatePlaylistNumberOfPlays():
    #function that calculates the total number of plays in the playlist
    totalPlays = 0
    scheduler.suspend_mainloop()
    for song in play_list.validFiles:
        if scheduler.userIntervention == True:
            # user changed something in the play_list that might affect the outcome of this loop
            scheduler.userIntervention = False
            break
        windowCascade.root.title("Calculating Playlist No. Of Plays: " + song.fileName)
        totalPlays+= song.NumberOfPlays
        scheduler.single_loop()  # this will make the main window responsive

    scheduler.resume_mainloop()

    windowCascade.root.title(Project_Title)
    return totalPlays

def calculatePlaylistFilesSize():
    # function that calculated the total size for all songs in the playlist
    totalSize = 0

    scheduler.suspend_mainloop()
    for song in play_list.validFiles:
        if scheduler.userIntervention == True:
            # user changed something in the play_list that might affect the outcome of this loop
            scheduler.userIntervention = False
            break
        windowCascade.root.title("Calculating Playlist File Size: " + song.fileName)
        totalSize+= song.fileSize
        scheduler.single_loop()  # this will make the main window responsive

    scheduler.resume_mainloop()
    windowCascade.root.title(Project_Title)
    return totalSize

def calculatePlaylistCutLength():
    # function that calculated the value of cutted length for the songs in the plaulist
    cutLength = 0

    scheduler.suspend_mainloop()
    for song in play_list.validFiles:
        if scheduler.userIntervention == True:
            # user changed something in the play_list that might affect the outcome of this loop
            scheduler.userIntervention = False
            break
        windowCascade.root.title("Calculating Playlist Cut Length: " + song.fileName)
        cutLength+= song.Length - (song.endPos-song.startPos)
        scheduler.single_loop()  # this will make the main window responsive

    scheduler.resume_mainloop()
    windowCascade.root.title(Project_Title)
    return cutLength

def findFavoriteGenre():
    ## function that determines which is the favorite genre in the playlist based on the listened time
    genres = {}

    scheduler.suspend_mainloop()
    for song in play_list.validFiles:
        if scheduler.userIntervention == True:
            # user changed something in the play_list that might affect the outcome of this loop
            scheduler.userIntervention = False
            break
        windowCascade.root.title("Finding Favorite Musical Genre: " + song.fileName)
        if song.Genre not in genres.keys():
            genres[song.Genre] = song.SongListenedTime
        else:
            genres[song.Genre] += song.SongListenedTime
        scheduler.single_loop()  # this will make the main window responsive

    scheduler.resume_mainloop()
    windowCascade.root.title(Project_Title)
    genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
    most_wanted = genres[0]
    return [str(most_wanted[0]), int(most_wanted[1])]

def findFavoriteTrack():
    # function that determines which is the favorite song in the playlist based on the listened time
    if len(play_list.validFiles) > 0:
        favoriteSong = play_list.validFiles[0]
        scheduler.suspend_mainloop()
        for song in play_list.validFiles:
            if scheduler.userIntervention == True:
                #user changed something in the play_list that might affect the outcome of this loop
                scheduler.userIntervention = False
                break
            windowCascade.root.title("Finding Favorite Song: " + song.fileName)
            if favoriteSong.SongListenedTime < song.SongListenedTime:
                favoriteSong = song
            scheduler.single_loop()  # this will make the main window responsive

        scheduler.resume_mainloop()
        windowCascade.root.title(Project_Title)
        return favoriteSong
    else:
        return "NA"

def findFavoriteArtist():
    # function that determines which is the favorite artist in the playlist based on the time listened on their tracks
    if len(play_list.validFiles) > 0:
        artists = [song.Artist for song in play_list.validFiles]
        uniqueArtists = set(artists)
        favoriteArtistListenedTime = 0
        favoriteArtist = artists[0]
        favoriteArtistNoOfPlays = 0

        scheduler.suspend_mainloop()
        for artist in uniqueArtists:
            windowCascade.root.title("Finding Favorite Artist: " + str(artist))
            calculatedArtistListenedTime = calculateArtistListenedTime(artist)
            if favoriteArtistListenedTime < calculatedArtistListenedTime:
                favoriteArtistListenedTime = calculatedArtistListenedTime
                favoriteArtist = artist
                favoriteArtistNoOfPlays = calculateArtistNoOfPlays(favoriteArtist)
            scheduler.single_loop()  # this will make the main window responsive

        scheduler.resume_mainloop()
        windowCascade.root.title(Project_Title)
        return [favoriteArtist, favoriteArtistListenedTime, favoriteArtistNoOfPlays]
    else:
        return "NA"

def findFavoriteSongOfArtist(Artist: str):
    #function that determines which is the favorite song in the playlist based on the time listened on the artist tracks
    artistSongs = list(filter(lambda song: song.Artist == Artist, play_list.validFiles))
    if len(artistSongs) > 0:
        mostListenedSong = artistSongs[0]

        scheduler.suspend_mainloop()
        for song in artistSongs:
            windowCascade.root.title("Finding Favorite Song of Artist: " + str(song.fileName))
            if mostListenedSong.SongListenedTime < song.SongListenedTime:
                mostListenedSong = song
            scheduler.single_loop()  # this will make the main window responsive

        scheduler.resume_mainloop()

        windowCascade.root.title(Project_Title)
        return song.Title
    else:
        return None

def calculateArtistListenedTime(Artist: str):
    # function that calculates the amount of time the user listened to given artist in the playlist
    artistSongs = list(filter(lambda song: song.Artist == Artist, play_list.validFiles))
    listenedTime = 0

    scheduler.suspend_mainloop()
    for song in artistSongs:
        windowCascade.root.title("Calculating Time Listened to Artist: " + str(song.fileName))
        listenedTime += song.SongListenedTime
        scheduler.single_loop()  # this will make the main window responsive

    scheduler.resume_mainloop()
    windowCascade.root.title(Project_Title)
    return listenedTime

def calculateArtistNoOfPlays(Artist: str):
    #function that calculates the number of song plays the user acumulated on a given artist in the playlist
    artistSongs = list(filter(lambda song: song.Artist == Artist, play_list.validFiles))
    noOfPlays = 0

    scheduler.suspend_mainloop()
    for song in artistSongs:
        windowCascade.root.title("Calculating Artist No. Of Plays: " + str(song.fileName))
        noOfPlays += song.NumberOfPlays
        scheduler.single_loop() # this will make the main window responsive

    scheduler.resume_mainloop()
    windowCascade.root.title(Project_Title)
    return noOfPlays

def getArtistMusicalGenre(Artist: str):
    #this function will return all musical genres from given artist within the playlist
    artistSongs = list(filter(lambda song: song.Artist == Artist, play_list.validFiles))
    musicalGenre = []

    scheduler.suspend_mainloop()
    for song in artistSongs:
        windowCascade.root.title("Finding Musical Genre of Artist: " + str(song.fileName))
        musicalGenre.append(song.Genre)
        scheduler.single_loop() # this will make the main window responsive

    scheduler.resume_mainloop()

    windowCascade.root.title(Project_Title)
    musicalGenre = list(set(musicalGenre))
    musicalGenre = " | ".join(musicalGenre)
    return musicalGenre

def getArtistNumberOfSongs(Artist: str):
    #this function will calculate the number of songs for given artist within the playlist
    artistSongs = list(filter(lambda song: song.Artist == Artist, play_list.validFiles))
    return len(artistSongs)

def exportPlaylistInfoToXls():
    #this function will generate / export a xls report about the playlist

    # Workbook() takes one, non-optional, argument
    # which is the filename that we want to create.
    playlistReportFilename = 'PlaylistReport.xlsx'
    try:
        workbook = xlsxwriter.Workbook(playlistReportFilename)

        # The workbook object is then used to add new
        # worksheet via the add_worksheet() method.
        worksheet = workbook.add_worksheet("Artist Report")

        # Use the worksheet object to write
        # data via the write() method.
        topRowFormat = workbook.add_format({'bold': True, 'font_color': 'orange', 'font_size': 12, 'align': 'center', 'bg_color':'EEEEEE', 'border':5, 'font_name': 'Consolas',
        'shrink': False, 'border_color': 'orange', 'text_wrap': True})
        regularRowFormat = workbook.add_format({'bold': False, 'font_color': 'black', 'font_size': 10, 'align': 'left', 'bg_color':'FFFFFF', 'border':1, 'font_name': 'Consolas',
        'shrink': False, 'text_wrap': True})

        #Artist Report Worksheet
        worksheet.write('A1', 'Artist', topRowFormat)
        worksheet.write('B1', 'Musical Genre', topRowFormat)
        worksheet.write('C1', 'Listened Time', topRowFormat)
        worksheet.write('D1', 'Number of Plays', topRowFormat)
        worksheet.write('E1', 'Favorite Song', topRowFormat)
        worksheet.write('F1', 'Number of Songs', topRowFormat)
        rowCounter = 2 #top row is already set above
        if len(play_list.validFiles) > 0:
            artists = [song.Artist for song in play_list.validFiles]
            uniqueArtists = set(artists)

            scheduler.suspend_mainloop()
            for artist in uniqueArtists:
                windowCascade.root.title("Writing to XLS report: " + str(artist))
                worksheet.write('A'+str(rowCounter), str(artist), regularRowFormat)
                worksheet.write('B'+str(rowCounter), str(getArtistMusicalGenre(artist)), regularRowFormat)
                worksheet.write('C'+str(rowCounter), str(formatTimeString(calculateArtistListenedTime(artist))).split('.')[0], regularRowFormat)
                worksheet.write('D'+str(rowCounter), str(calculateArtistNoOfPlays(artist)), regularRowFormat)
                worksheet.write('E'+str(rowCounter), str(findFavoriteSongOfArtist(artist)), regularRowFormat)
                worksheet.write('F'+str(rowCounter), str(getArtistNumberOfSongs(artist)), regularRowFormat)
                rowCounter+=1
                windowCascade.root.title("Exporting report for: " + artist)
                scheduler.single_loop()

            scheduler.resume_mainloop()

        worksheet.set_column('A:B', 40)
        worksheet.set_column('C:D', 20)
        worksheet.set_column('E:E', 40)
        worksheet.set_column('F:F', 20)

        #Song Report Worksheet
        worksheet = workbook.add_worksheet("Song Report")
        worksheet.write('A1', 'Artist', topRowFormat)
        worksheet.write('B1', 'Title', topRowFormat)
        worksheet.write('C1', 'Genre', topRowFormat)
        worksheet.write('D1', 'Listened Time', topRowFormat)
        worksheet.write('E1', 'Number of Plays', topRowFormat)
        rowCounter=2#top row is already set above

        scheduler.suspend_mainloop()

        for song in play_list.validFiles:
            if scheduler.userIntervention == True:
                #user changed something in the play_list that might affect the outcome of this loop
                scheduler.userIntervention = False
                break
            windowCascade.root.title("Writing to XLS report: " + song.fileName)
            worksheet.write('A'+str(rowCounter), song.Artist, regularRowFormat)
            worksheet.write('B'+str(rowCounter), song.Title, regularRowFormat)
            worksheet.write('C'+str(rowCounter), song.Genre, regularRowFormat)
            worksheet.write('D'+str(rowCounter), str(formatTimeString(song.SongListenedTime)).split('.')[0], regularRowFormat)
            worksheet.write('E'+str(rowCounter), str(song.NumberOfPlays), regularRowFormat)
            rowCounter+=1
            windowCascade.root.title("Exporting report for: " + song.Artist + " - " + song.Title)
            scheduler.single_loop() # this will make the main window responsive

        scheduler.resume_mainloop()

        windowCascade.root.title(Project_Title)
        worksheet.set_column('A:A', 40)
        worksheet.set_column('B:B', 60)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 15)
        workbook.close()
    except Exception as exp:
        text = "Unable to create Report due to: " + str(exp)
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
    # Finally, close the Excel file
    # via the close() method.
    else:
        os.startfile(playlistReportFilename)
    windowCascade.root.title(Project_Title)

def showPlaylistInfo():
    #this function will calculate and display information about the exsting playlist
    if(len(play_list.validFiles) > 0):
        favoriteSong = findFavoriteTrack()
        favoriteArtist = findFavoriteArtist()
        text = ("OVERALL:" +"\n" \
        +"Number of Files:   " + str(len(play_list.validFiles)) +"\n" \
        +"Number of Plays:   " + str(calculatePlaylistNumberOfPlays())+ "\n" \
        +"Total Length:      " + formatTimeString(int(play_list.playTime)) + "\n" \
        +"Cutted Length:     " + formatTimeString(int(calculatePlaylistCutLength())) + "\n" \
        +"Playable Length:   " + formatTimeString(int(play_list.playTime - calculatePlaylistCutLength())) + "\n" \
        +"Total Size:        " + str(round(calculatePlaylistFilesSize())) + "MB\n" \
        +"Time Listened:     " +formatTimeString(int(play_list.PlaylistListenedTime)) + "\n" \
        +"Created On:        " +str(play_list.BornDate)[:19] + "\n" \
        +"\nFAVORITE GENRE:\n" \
        +"Favorite Genre:    " + findFavoriteGenre()[0] + "\n" \
        +findFavoriteGenre()[0] + " listened:   " + formatTimeString(findFavoriteGenre()[1]) + "\n")
        if isinstance(favoriteSong, Song):
            text+="\nMOST LISTENED TRACK:\n" \
            +favoriteSong.fileName + "\n" \
            +"Listen Time:       " + formatTimeString(int(favoriteSong.SongListenedTime)) + "\n" \
            +"Number of Plays:   " + str(favoriteSong.NumberOfPlays) + "\n" \
            +"Song Rating:       " + "NA" if favoriteSong.Rating==0 else str(favoriteSong.Rating)

        if favoriteArtist!="NA":
            text += "\n\nMOST LISTENED ARTIST:\n" \
            +favoriteArtist[0] + "\n" \
            +"Listen Time:       " + formatTimeString(int(favoriteArtist[1])) + "\n" \
            +"Number of Plays:   " + str(favoriteArtist[2]) + "\n"
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None),
                     Button2_Functionality=ButtonFunctionality("Generate Playlist Report",
                           exportPlaylistInfoToXls), windowTitle = "Playlist Info")
    else:
        WindowDialog("Playlist is empty.", Button1_Functionality=ButtonFunctionality("OK", None),
                     windowTitle="Playlist Info")

def focusListbox(event):
    listbox.focus()
    listbox.see(play_list.currentSongIndex)  # Makes sure the given list index is visible. You can use an integer index,
    listbox.selection_clear(0, tk.END)  # clear existing selection
    listbox.select_set(play_list.currentSongIndex)
    listbox.activate(play_list.currentSongIndex)

def focusWindow(event):
    windowCascade.root.focus()

def windows_focus_switch(event):
    #this function will ensure that no matter which main window element is being focused
    #the listbox does not lose its highlight and selection set
    focusListbox(event)

def packPositionListScrolOptionProgRadio():
    #Function called only at the start, to place the listbox, scrollbar, combobox, radiobuttons, progressbar,
    #Here are set position, events, controls, styling for listbox, progressbar, scrollbar, option, radiobuttons

    SearchFrame.pack(side = tk.LEFT)
    labelSearch.pack(side = tk.LEFT)
    searchValue.pack(side = tk.RIGHT)
    ClearSearchButton.pack(side = tk.RIGHT)

    listbox.pack(side = tk.LEFT, padx=2, pady=6) #this will place listbox on the leftside of the FRAME
    listbox.bind('<Double-Button>', elementPlaylistDoubleClicked)
    listbox.bind('<ButtonPress-3>', rightClickListboxElement)
    listbox.bind('<<ListboxSelect>>', list_selected_item)
    listbox.bind("<Return>", elementPlaylistDoubleClicked)
    listbox.bind("<Key>", listboxShortcuts)
    listbox.bind("<Escape>", focusWindow)

    windowCascade.root.bind("<Return>", pressedEnter)
    windowCascade.root.bind("<Shift_R>", pressedShiftRight)
    windowCascade.root.bind("<Control_R>", pressedCtrlRight)
    windowCascade.root.bind("<Key>", pressedKeyShortcut)
    windowCascade.root.bind("<Shift_L>", pressedShiftLeft)
    windowCascade.root.bind("<Control_L>", pressedCtrlLeft)
    windowCascade.root.bind("<KeyRelease-]>", squareBracketsReleased)
    windowCascade.root.bind("<KeyRelease-[>", squareBracketsReleased)
    windowCascade.root.bind("<Delete>", pressedDelete)
    windowCascade.root.bind('<ButtonPress-3>', rightClickOnWindow)
    windowCascade.root.bind('<Up>', focusListbox)
    windowCascade.root.bind('<Down>', focusListbox)
    windowCascade.root.bind('<Tab>', windows_focus_switch)

    #these are used for instant search:
    searchValue.bind("<KeyRelease>", showSearchResults)
    searchValue.bind("<Escape>", focusWindow)

    scroll.config(command=listbox.yview)

    # this will place scrollbar on the right side of FRAME, if width is adjusted, they will be next to each other
    scroll.pack(side = tk.RIGHT, fill=tk.Y)

    progress.bind("<Button>", navigationSound)
    progress.place(x=progressBarMargin, y=80)

    radioButtonLineHeight = 390
    labelSongRating.place(x=10, y=radioButtonLineHeight)
    RadioButtonsPosX=labelSongRating.winfo_reqwidth()+10 #10 - the X margin of the label
    R1.place(x=RadioButtonsPosX, y=radioButtonLineHeight)
    R2.place(x=RadioButtonsPosX+35, y=radioButtonLineHeight)
    R3.place(x=RadioButtonsPosX+70, y=radioButtonLineHeight)
    R4.place(x=RadioButtonsPosX+105, y=radioButtonLineHeight)
    R5.place(x=RadioButtonsPosX+140, y=radioButtonLineHeight)

    VolumeScale.bind("<ButtonRelease-1>", setLinearVolume)

    calculateScreenHeightWidth() #this will draw the listbox

def buttonAdjustments(): #this function will adjust some buttons (which are near labels) when the font gets changed
    # Adjust these elements
    radioButtonLineHeight = 390
    labelSongRating.place(x=10, y=radioButtonLineHeight)
    RadioButtonsPosX = labelSongRating.winfo_reqwidth() + 5 #the X margin of the label
    R1.place(x=RadioButtonsPosX, y=radioButtonLineHeight)
    R2.place(x=RadioButtonsPosX + 35, y=radioButtonLineHeight)
    R3.place(x=RadioButtonsPosX + 70, y=radioButtonLineHeight)
    R4.place(x=RadioButtonsPosX + 105, y=radioButtonLineHeight)
    R5.place(x=RadioButtonsPosX + 140, y=radioButtonLineHeight)

def setLinearVolume(event): #function called when moving the Volume Slider
    global play_list
    play_list.VolumeLevel = VolumeScale.get() / 100
    if pygame.mixer.get_init():
        if play_list.currentSongPosition - play_list.validFiles[play_list.currentSongIndex].startPos > \
                play_list.validFiles[play_list.currentSongIndex].fadein_duration and play_list.currentSongPosition < \
                        play_list.validFiles[play_list.currentSongIndex].endPos - play_list.validFiles[
                    play_list.currentSongIndex].fadeout_duration:
            pygame.mixer.music.set_volume(play_list.VolumeLevel)

def showCuttingTool(index=None):
    if listbox.size() and listBox_Song_selected_index!= None:
        if windowCascade.CuttingTool == None:
            if play_list.useCrossFade == False:
                CuttingTool(windowCascade.root, index)
            else:
                text = ("Sorry!\n\nYou cannot use this feature while cross-fading is enabled.\n\n"+
                "Cross-fading adjust the length of your tracks so that you won't hear gaps between them.")
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
        else:
            text = "Cutting Tool Window is already opened."
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
    else:
        text = "Use the playlist to select a song."
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

def showSleepingTool():
    if windowCascade.SleepingTool == None:
        SleepingTool(windowCascade.root)
    else:
        text = "Sleeping Tool Window is already opened."
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")

def fontTitleTransition(Message):
    #this function will handle transitions done on the application title
    Message = list(Message)
    for x in range(0, len(Message)):
        if(x+1<len(Message)):
            aux = Message[x+1]
            Message[x] = Message[x+1]
            Message[x+1] = aux
        else:
            aux = Message[0]
            Message[x] = Message[0]
            Message[0] = aux
    return "".join(Message)

def fontSeparatedTransition(Message):
    #this function will handle font-separation transition/animation
    Message = list(Message)
    for x in range(0, len(Message)):
        if Message[x] == "_":
            if x+1 < len(Message):
                aux = Message[x+1]
                Message[x+1] = Message[x]
                Message[x] = aux
            else:
                Message ="".join(Message)
                Message = Message.split("_")
                Message = Message[0]
                Message = "_" + Message
            break
    return "".join(Message)

def fontTypeWritingTransition(Message):
    #this function will handle type-writing transition/animation
    if Message == play_list.validFiles[play_list.currentSongIndex].fileName:
        Message = ""
    else:
        Message += play_list.validFiles[play_list.currentSongIndex].fileName[len(Message)]
    return Message

def fadein(Position):
    #this function will handle fade-in
    pygame.mixer.music.set_volume((Position/play_list.validFiles[play_list.currentSongIndex].fadein_duration)*play_list.VolumeLevel) #multiplied to VolumeLevel to make sure it doesn't pass the current volume level

def fadeout(Position):
    # this function will handle fade-out
    pygame.mixer.music.set_volume((Position/play_list.validFiles[play_list.currentSongIndex].fadeout_duration)*play_list.VolumeLevel) #multiplied to VolumeLevel to make sure it doesn't pass the current volume level

def computeTimeToSeconds(time):
    #this function is used to convert time string to seconds
    time = time.split(":")
    returnVal = 0
    for entity in time:
        if entity!="":
            index = time.index(entity)
            try:
                entity=int(entity)
            except Exception:
                text = "An invalid value was entered."
                WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
                return -1
            else:
                returnVal += entity* (60**(len(time)-1-index))
        else:
            text = "Miss-use of ':' symbol, the entered value is invalid."
            WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle = "Information")
            return -1
    return returnVal

def dragging(event):
    #this function will handle dragging.
    #when window gets drag on the screen, we should update the play_list data to know where to
    #place the window next time we load the play_list
    if event.widget is windowCascade.root:  # do nothing if the event is triggered by one of root's children
        play_list.playerXPos = windowCascade.root.winfo_x()
        play_list.playerYPos = windowCascade.root.winfo_y()

def mainWindowUpdate():
    #this function will attempt to refresh / update the window
    #the more often called the more responsive it is
    try:#without this try-except block the window will freeze.
        windowCascade.root.update()  # Force an update of the GUI
    except Exception as exp: pass  #exception will be generated if the window was closed in the meantime.

searchIndex = None

def showSearchResults(event):
    #this function will show search results in the listbox when user searched or something
    global searchIndex
    if event.keysym_num > 0 and event.keysym_num < 60000 or \
                    event.keysym_num == 65288 or event.keysym_num == 65535: #BACKSPACE or DELETE
        #if the key pressed is a printable character that could be in the name of the searched item
        #or key pressed is backspace or delete
        global listBox_Song_selected_index
        if len(searchValue.get()) > 0:
            value = searchValue.get().lower()
            #result = [item for item in play_list.validFiles if value in item.fileName.lower()]
            #result = [str(play_list.validFiles.index(item)) + ". " + item.fileName for item in play_list.validFiles if value in item.fileName.lower()]
            result = []
            for element in play_list.validFiles:
                mainWindowUpdate() #this will make the window and the search form responsive
                if searchValue.get().lower() != value:
                    #abort the search if user is still typing
                    return
                if value in element.fileName.lower():
                    result.append(str(play_list.validFiles.index(element)) + ". " + element.fileName)

            if len(result) > 0:
                listbox.delete(0, tk.END)
                listbox.insert(tk.END, *result) #full list insert
                #Inserting of elements 1 by 1 within the FOR loop is considerably slower than full list insert
                #for item in result:
                #    listbox.insert(tk.END, str(play_list.validFiles.index(item)) + ". " + item.fileName)
            else:
                listbox.delete(0, tk.END)
        else:
            displayElementsOnPlaylist()
            showCurrentSongInList()
            searchIndex=play_list.currentSongIndex
        listbox.selection_clear(0, tk.END)  # clear existing selection
        listbox.select_set(listBox_Song_selected_index)
        listbox.activate(listBox_Song_selected_index)
        listbox.see(listBox_Song_selected_index)

def playPreviousSearchItem():
    #this function will be called when hitting R_Shift in searchbar (shortcut for playing Previous Song)
    #here we'll determine which next search match we should play
    global searchIndex
    global play_list
    global listBox_Song_selected_index
    elements = listbox.get(0, tk.END)
    if len(elements) > 0:
        if searchIndex == None:
            searchIndex = len(elements) - 1
        elif searchIndex - 1 >= 0:
            searchIndex -= 1
        else:
            searchIndex = len(elements)-1
        real_index = elements[searchIndex]
        real_index = real_index.split(". ")
        real_index = real_index[0]
        listBox_Song_selected_index = searchIndex
        listbox.selection_clear(0, tk.END)  # clear existing selection
        listbox.select_set(listBox_Song_selected_index)
        listbox.activate(listBox_Song_selected_index)
        listbox.see(listBox_Song_selected_index)
        play_list.currentSongIndex = int(real_index)
        if play_list.danthologyMode == False:
            play_list.currentSongPosition = 0
        play_music()

def playNextSearchItem():
    #this function will be called when hitting Enter in searchbar (shortcut for playing Next Song)
    #here we'll determine which next search match we should play
    global searchIndex
    global play_list
    global listBox_Song_selected_index
    elements = listbox.get(0,tk.END)
    if len(elements) > 0:
        if searchIndex == None:
            searchIndex = 0
        elif searchIndex + 1 < len(elements):
            searchIndex += 1
        else:
            searchIndex = 0
        real_index = elements[searchIndex]
        real_index = real_index.split(". ")
        real_index = real_index[0]
        listBox_Song_selected_index = searchIndex
        listbox.selection_clear(0, tk.END)  # clear existing selection
        listbox.select_set(listBox_Song_selected_index)
        listbox.activate(listBox_Song_selected_index)
        play_list.currentSongIndex = int(real_index)
        if play_list.danthologyMode == False:
            play_list.currentSongPosition = 0
        play_music()

def SearchBoxClear():
    #this function will be called when hitting the clear button for the searchbox
    if searchValue.get() != "":
        searchValue.delete(0, tk.END)
        searchIndex=play_list.currentSongIndex
        displayElementsOnPlaylist()
        showCurrentSongInList()

def visitDownloadPage():
    # this function will open up a webpage in the default web browser
    webbrowser.open('https://github.com/dragos-vacariu/Portable-Downloads/tree/main/PyPlay%20MP3%20Player')

def visitOfficialWebpage():
    #this function will open up a webpage in the default web browser
    webbrowser.open('https://dragos-vacariu.github.io/Html-Projects/Web%20Templates/project40%20python%20mp3%20player%20webpage/index.html')

def createMenuBar():
    #this function will set up the menubar

    global  menubar
    menubar.root = tk.Menu(windowCascade.root)
    filemenu = tk.Menu(menubar.root, tearoff=0)
    filemenu.add_command(label="Open Files", command=load_file)
    filemenu.add_command(label="Open Directory", command=load_directory)
    filemenu.add_separator()
    filemenu.add_command(label="Save Playlist As", command=save_playlist)
    filemenu.add_command(label="Clear Playlist", command=new_playlist)
    filemenu.add_separator()
    filemenu.add_command(label="Save and Exit", command=on_closing)

    menubar.root.add_cascade(label="File", menu=filemenu)
    setattr(menubar, "file_menu", filemenu)

    playback_menu = tk.Menu(menubar.root, tearoff=0)
    playback_menu.add_command(label="Play/Pause", command=pause_music)
    playback_menu.add_command(label="Stop", command=stop_music)
    playback_menu.add_command(label="Reset Track", command=resetTrack)
    playback_menu.add_command(label="Next Track", command=next_song)
    playback_menu.add_command(label="Previous Track", command=previous_song)
    playback_menu.add_separator()
    playback_menu.add_command(label="Mute/Unmute", command=mutePlayback)
    playback_menu.add_separator()
    playback_menu.add_command(label="Show Current Track", command=showCurrentSongInList)
    playback_menu.add_separator()
    playback_menu.add_command(label="Cancel Current Operation", command=cancelOperation)
    menubar.root.add_cascade(label="Playback", menu=playback_menu)
    setattr(menubar, "playback_menu", playback_menu)

    # Creating preferences menu
    preferences_menu = tk.Menu(menubar.root, tearoff=0)

    # creating view_menu
    view_menu = tk.Menu(preferences_menu, tearoff=0)
    view_menu.add_command(label='Compact View', command=seeCompact)
    view_menu.add_command(label='Playlist View', command=seePlaylist)

    # Attach view_menu to View Label which is part of preferences_menu
    preferences_menu.add_cascade(label="View", menu=view_menu)
    setattr(menubar, "preferences_view_menu", view_menu)
    # creating skin_menu
    skin_menu = tk.Menu(preferences_menu, tearoff=0)

    for index in range(0, len(skinOptions)):
        skin_menu.add_command(label=skinOptions[index].skin_name,
                              command=skinOptions[index].changingSkin)

    # Attach view_menu to View Label which is part of preferences_menu
    preferences_menu.add_cascade(label="Skins", menu=skin_menu)
    setattr(menubar, "preferences_skin_menu", skin_menu)
    updateSkinMenuLabels()

    # creating skin_menu
    sort_menu = tk.Menu(preferences_menu, tearoff=0)

    sort_menu.add_command(label='Sort By Name', command=sortByFileName)
    sort_menu.add_command(label='Sort By Name Reversed', command=sortByFileNameReversed)
    sort_menu.add_command(label='Sort Randomize', command=sortRandomized)
    sort_menu.add_command(label='Sort By Rating', command=sortByRating)
    sort_menu.add_command(label='Sort By Rating Reversed', command=sortByRatingReversed)
    sort_menu.add_command(label='Sort By Length', command=sortByLength)
    sort_menu.add_command(label='Sort By Length Reversed', command=sortByLengthReversed)
    sort_menu.add_command(label='Sort By Genre', command=sortByGenre)
    sort_menu.add_command(label='Sort By Genre Reversed', command=sortByGenreReversed)
    sort_menu.add_command(label='Sort By No. Of Plays', command=sortByNoOfPlays)
    sort_menu.add_command(label='Sort By No. Of Plays Reversed', command=sortByNoOfPlaysReversed)
    sort_menu.add_command(label='Sort By Year', command=sortByYear)
    sort_menu.add_command(label='Sort By Year Reversed', command=sortByYearReversed)
    sort_menu.add_command(label='Sort By Album', command=sortByAlbum)
    sort_menu.add_command(label='Sort By Album Reversed', command=sortByAlbumReversed)
    sort_menu.add_command(label='Sort By Title', command=sortByTitle)
    sort_menu.add_command(label='Sort By Title Reversed', command=sortByTitleReversed)
    sort_menu.add_command(label='Sort By Least Listened', command=sortByListenedTime)
    sort_menu.add_command(label='Sort By Most Listened', command=sortByListenedTimeReversed)
    sort_menu.add_command(label='Sort By Most Recent', command=sortByFileMostRecent)
    sort_menu.add_command(label='Sort By Modified Date', command=sortByFileModifiedDate)

    # Attach view_menu to View Label which is part of preferences_menu
    preferences_menu.add_cascade(label="Sort List", menu=sort_menu)
    setattr(menubar, "preferences_sort_menu", sort_menu)
    # Attach option to Preferences Menu
    preferences_menu.add_command(label="Customize", command=showCustomizeWindow)

    # attach Preferences to menubar
    menubar.root.add_cascade(label="Preferences", menu=preferences_menu)
    setattr(menubar, "preferences_menu", preferences_menu)

    tools_menu = tk.Menu(menubar.root, tearoff=0)
    tools_menu.add_command(label="Sleep/Wakeup Timers", command=showSleepingTool)
    tools_menu.add_command(label="MP3 Tag Modifier Tool", command=showMp3TagModifierWindow)
    tools_menu.add_command(label="Slideshow", command=showSlideshowWindow)
    tools_menu.add_command(label="Playback Cutter", command=showCuttingTool)
    menubar.root.add_cascade(label="Tools", menu=tools_menu)
    setattr(menubar, "tools_menu", tools_menu)

    misc_menu = tk.Menu(menubar.root, tearoff=0)
    misc_menu.add_command(label="Search Lyrics Online", command=showGrabLyricsWindow)
    misc_menu.add_command(label="Read Artist Biography", command=showArtistBioWindow)
    misc_menu.add_separator()
    misc_menu.add_command(label="Generate Playlist Report", command=exportPlaylistInfoToXls)
    misc_menu.add_command(label="Resynchronize Playlist", command=checkResynchronizePlaylist)
    misc_menu.add_command(label="Flagged Files Report", command=showFlaggedMp3Files)
    menubar.root.add_cascade(label="Misc", menu=misc_menu)
    setattr(menubar, "misc_menu", misc_menu)

    helpmenu = tk.Menu(menubar.root, tearoff=0)
    helpmenu.add_command(label="About", command=showAboutWindow)
    helpmenu.add_command(label="Keyboard Shortcuts", command=showKeybordShortcuts)
    helpmenu.add_separator()
    helpmenu.add_command(label="Check for latest version", command=visitDownloadPage)
    helpmenu.add_command(label="Visit official webpage", command=visitOfficialWebpage)
    menubar.root.add_cascade(label="Help", menu=helpmenu)
    setattr(menubar, "help_menu", helpmenu)

    windowCascade.root.config(menu=menubar.root)

def DragAndDrop(event):
    #this function will handle drag and drop. Designed for tkinterdnd2 but not supported by pyinstaller or py2exe
    data = event.data
    data = windowCascade.root.tk.splitlist(data) #converting whatever string we get from drag&drop into a list
    
    mp3_files = []
    for element in data:
        if os.path.isfile(element):
            if element.endswith(".mp3"):
                mp3_files.append(element)
            elif element.endswith(".pypl"):
                loadPlaylistFile(element)
                displayElementsOnPlaylist()
        elif os.path.isdir(element): 
            load_directory(element)
    if len(mp3_files) > 0:
        load_file(mp3_files)
    
def formatTimeString(time):
    # this function will format seconds in time string
    seconds_to_minute = 60
    seconds_to_hour = 60 * seconds_to_minute
    seconds_to_day = 24 * seconds_to_hour

    days = time // seconds_to_day
    time %= seconds_to_day

    hours = time // seconds_to_hour
    time %= seconds_to_hour

    minutes = time // seconds_to_minute
    time %= seconds_to_minute

    seconds = time
    string_value = ""

    if int(hours) < 10 and int(hours) >=1:
        string_value = "0"+ str(int(hours)) + ":"
    elif int(hours) == 0:
        string_value = "00:"
    else:
        string_value = str(int(hours)) + ":"

    if int(minutes) < 10 and int(minutes) >=1:
        string_value += "0"+ str(int(minutes)) + ":"
    elif int(minutes) == 0:
        string_value += "00:"
    else:
        string_value += str(int(minutes)) + ":"

    if int(seconds) < 10 and int(seconds) >=1:
        string_value += "0"+ str(int(seconds))
    elif int(seconds) == 0:
        string_value += "00"
    else:
        string_value += str(int(seconds))

    if int(days) > 0:
        string_value = str(days) + " days, " + string_value

    return string_value

def pressedHotkey(key):
    global hotkeyMonitor
    if key == pynput.keyboard.Key.media_play_pause:
        hotkeyMonitor.playPauseTrigger = True
    elif key == pynput.keyboard.Key.media_previous:
        hotkeyMonitor.previousSongTrigger = True
    elif key == pynput.keyboard.Key.media_next:
        hotkeyMonitor.nextSongTrigger = True

def checkOpenFile(data):
    """This function will handle opening files using commandline arguments argv"""
    global play_list
    data = formatSlashesInFilePath(data)
    if len(data) > 0:
        #this indeterminate loop shall not suspend the scheduler main loop, and should not be used
        #for single looping the scheduler, as this function may get called before everything in the gui
        #would exist. That also includes the scheduler. The scheduler gets created only for the main instance.

        for element in play_list.validFiles:
            if element.filePath == data:
                return play_list.validFiles.index(element)

        #if reached here, it means song not in the list
        song = Song(data)
        play_list.validFiles.append(song)
        del song
        return len(play_list.validFiles) - 1 #the song will be added at the end of the list


shared_memory_buffer = SharedMemoryDict(name='config', size=1024)
share_memory_separator = "$<?*@>#sep" #a separator for string elements stored in shared_memory_dict
#something uncommon so that it will not affect possible filepaths

def checkReadDataFromSharedMemory():
    #this function will get called / checked regularly within the Main Instance
    global listBox_Song_selected_index
    global play_list
    try:
        if shared_memory_buffer["processes"]  > ALLOWED_AMOUNT_OF_APP_INSTANCES:
            #if multiple instances of the script were opened we will monitor when they get closed
            shared_memory_buffer["processes"] = getNumberOfInstancesRunning()
        elif shared_memory_buffer["data"] != "" and shared_memory_buffer["processes"] == ALLOWED_AMOUNT_OF_APP_INSTANCES:
            #if the other instances of the program we're closed, and they left
            #data in the shared_memory. we'll try to use it to update the play_list

            elements = shared_memory_buffer["data"].split(share_memory_separator)
            for index in range(0, len(elements)-1):
                #the main window will remain responsive in checkOpenFile
                currentSize = len(play_list.validFiles) 
                added_song_index = checkOpenFile(elements[index])
                if index == 0:
                    #it's possible that user opened multiple selected files using pyplay as default app
                    #if multiple elements were found only hit play on the first one
                    play_list.currentSongIndex = added_song_index
                    play_list.currentSongPosition = 0
                    listBox_Song_selected_index = play_list.currentSongIndex
                    play_music()
                if currentSize < len(play_list.validFiles): 
                    #if we added a song, we will insert it in the listbox
                    listbox.insert(len(play_list.validFiles) - 1,
                                   str(len(play_list.validFiles) - 1) + ". " + play_list.validFiles[len(play_list.validFiles) - 1].fileName)
            showCurrentSongInList()
            shared_memory_buffer["data"] = ""
    except Exception as exp:
        #enter here if the item key is not yet defined within the Main Instance
        shared_memory_buffer["data"] = ""
        shared_memory_buffer["processes"] = getAllowedInstancesOnApp()

def storeDataToSharedMemory(value):
    #this function will be called in case a secondary instance of the program gets created
    #if the secondary instance contain sys.argv[1] meaning the user would want to open a file
    #we will ensure that we load the file into the running instance and then kill the secondary instance
    try:
        # shared_memory_buffer will allow storing value amongst separate instances of the program
        shared_memory_buffer["data"] += value + share_memory_separator
        shared_memory_buffer["processes"] += 1
    except:
        #if item/key is not defined in the it should throw an exception
        #initialize the items/keys used for shared memory
        shared_memory_buffer["data"] = value
        shared_memory_buffer["processes"] = getAllowedInstancesOnApp() + 1

def storeArgvForMainInstanceToFile(): #NOT USED - SHARED MEMORY FUNCTIONS ARE USED INSTEAD
    """Function used for storing cmd argv to a file in case user decides to open an .mp3 from explorer
    using context menu. This way we only need to read the argv from the new script instance, then we can
    load it into the existing script instance and close the other script instance."""
    f = open(dataTransferFileLocation, "w")
    f.write(sys.argv[1])
    f.close()

def readFileArgvFromClosingInstance(): #NOT USED - SHARED MEMORY FUNCTIONS ARE USED INSTEAD
    """Function used for read cmd argv from a file in case user decides to open an .mp3 from explorer
    using context menu. This way we only need to read the argv from the new script instance, then we can
    load it into the existing script instance and close the other script instance."""

    if os.path.isfile(dataTransferFileLocation):
        f = open(dataTransferFileLocation, "r")
        if len(sys.argv) > 1:
            sys.argv[1] = f.read()
        else:
            sys.argv.append(f.read())
        checkOpenFileFromArgv()
        play_music()
        displayElementsOnPlaylist()
        showCurrentSongInList()
        f.close()
        os.remove(dataTransferFileLocation)

def positionTkWidgetsVertically(xPos:int, upperElementReference, elementToBePlaced, margin=0):
    #function to place/position tk widget items vertically

    #NOTE: the upperElementReference is a frame
    #they need to be resized based on the children they hold before
    #being passed to this function.

    if hasattr(upperElementReference, "place_info") == True and \
        hasattr(upperElementReference, "winfo_reqheight") == True and \
        hasattr(elementToBePlaced, "place") == True:
        yPos = int(upperElementReference.place_info()["y"]) + upperElementReference.winfo_reqheight() + margin
        elementToBePlaced.place(x = xPos, y = yPos)

def calculateResizeWindow(window: tk, element_list: list, margin=0):
    #function to resize the given window based on a list of elements
    #if the elements are longer than the current size of the window, the size will be
    #readjusted to fit the content

    #The provided list of elements should include the rightmost and bottom last. If the elements
    #vary in size based on skin settings you can include more from both in the selection to
    # ensure the proper computation / resizing.

    #NOTE: the elements included in the list need to be children of the window,
    #in case of frame - they need to be resized based on the children they hold before
    #being passed to this function.

    if (type(margin) != int):
        margin = 0
    if isinstance(window, TkinterDnD.Tk) or isinstance(window, tk.Tk) or isinstance(window, tk.Toplevel):
        window_width = int(window.winfo_geometry().split("x")[0])
        window_height = int(window.winfo_geometry().split("x")[1].split("+")[0])
        for item in element_list:
            if item in window.winfo_children():
                if item.winfo_reqwidth() + int(item.place_info()["x"]) > window_width:
                    window_width = item.winfo_reqwidth() + int(item.place_info()["x"]) + margin
                if item.winfo_reqheight() + int(item.place_info()["y"]) > window_height:
                    window_height = item.winfo_reqheight() + int(item.place_info()["y"]) + margin

        geometry = str(window_width) + "x" + str(window_height) + "+" + \
                window.winfo_geometry().split("+")[1] + "+"+ window.winfo_geometry().split("+")[2]
        window.geometry(geometry)

def getAllowedInstancesOnApp():
    #this function will be used to get the maximum allowed of instances/processes for the application
    #we only want to run the application once, but if the application is run via Python using the .py file
    #then we don't have separate processes.

    #But if the application is .exe run directly by the OS, then we have proccesses defined.

    if scriptFileName.endswith(".exe") == True:
        # if script is .exe it means the system created the processes before running this function
        
        # IMPORTANT: For PyInstaller executables we need to check if we have 2 instances because there will 
        # be 2 processes on the .exe one for the pynput keyboard listener, 
        # and another one for the tkinter mainloop
        
        #make sure to change the statement below to 'return  2'
        
        return 1
    else:
        #application run via python
        return 0 #no separate process outside python

def getNumberOfInstancesRunning():
    #this function will monitor how many instances of the app are currently running

    instances = 0
    try:
        for process in psutil.process_iter():
            if process.name().startswith(scriptFileName):
                #should enter here if .exe process found
                instances += 1
            elif process.name().startswith('python'):
                #if python process found
                if len(process.cmdline()) > 1 and scriptFileName in process.cmdline()[1] and process.pid != os.getpid():
                    #enter here if the .py script is ran via python.exe
                    instances += 1
    except:
        #the statements above could throw and exception if the process we're looking at got closed
        #if the process got closes we don't really care.
        pass
    return instances

ALLOWED_AMOUNT_OF_APP_INSTANCES = getAllowedInstancesOnApp()

def isInstanceRunning():
    #this function will be run first - right after opening the program.
    #we'll determine if there are any other instances of the same app running
    instances = getNumberOfInstancesRunning()

    if instances > ALLOWED_AMOUNT_OF_APP_INSTANCES:
        if len(sys.argv) < 2:
            #if argv has only 1 argument it means user just opened a second instance without any use.
            messagebox.showinfo("Information", "PyPlay Mp3 Player is already opened.")
        else:
            #when user attempts to open a second instance but with some arguments it should mean an
            #attempt to open a file or group of files. We will ensure we open those files in the primary
            #instance. To do that we'll send the argv to a common shared memory amonst all instances
            storeDataToSharedMemory(sys.argv[1])
        return True
    else:
        return False

appRunningStatus = isInstanceRunning()

if appRunningStatus == True:
    #close the app
    sys.exit()

else:
    #Load backup if possible
    if os.path.exists(automaticallyBackupFile):
        loadPlaylistFile(automaticallyBackupFile)

    #If a file was opened using pyplay
    if len(sys.argv) > 1:
        play_list.currentSongIndex = checkOpenFile(sys.argv[1])
        play_list.currentSongPosition = 0
        listBox_Song_selected_index = play_list.currentSongIndex

    #================================================================================
    #UNCOMMENT THE FOLLOWING LINE IF TKDND2 IS NOT SUPPORTED WITH PYINSTALLER OR PY2EXE
    #windowCascade.root = tk.Tk()

    #COMMENT THE FOLLOWING 3 LINES IF TKDND2 IS NOT SUPPORTED WITH PYINSTALLER OR PY2EXE
    windowCascade.root = TkinterDnD.Tk()
    windowCascade.root.drop_target_register(DND_FILES)
    windowCascade.root.dnd_bind('<<Drop>>', DragAndDrop)
    #================================================================================

    Project_Title = "   PyPlay MP3 Player in Python     "
    windowCascade.root.title(Project_Title)

    windowCascade.root.geometry(str(play_list.playerWidth) + "x" + str(play_list.playerHeight) + "+" + str(play_list.playerXPos) + "+" + str(play_list.playerYPos)) #resize and reposition the window
    windowCascade.root.protocol("WM_DELETE_WINDOW", on_closing) #delete the window when clicking cancel, on closing is the function to deal with it

    windowCascade.root.bind('<Configure>', dragging)

    # Creating the StringVars and loading the skin information
    SkinColor = StringVar()
    allButtonsFont = StringVar()
    fontColor = StringVar()
    labelBackground = StringVar()

    SkinColor.set(play_list.skin_theme.background_color)
    labelBackground.set(play_list.skin_theme.label_bg_color)
    labelTextColor = play_list.skin_theme.getLabelTextColor()

    allButtonsFont.set(play_list.skin_theme.font)
    fontColor.set(play_list.skin_theme.button_font_color)
    backgroundFile = play_list.skin_theme.background_image

    #adding userColors to our existing list
    custom_color_list += play_list.userCreatedColors

    createMenuBar() #this will create the menubar
    updateViewMenuLabels() #this will update the view menu labels

    if os.path.isfile(playerIcon):
        windowCascade.root.wm_iconbitmap(playerIcon)
    else:
        text = ("File: \n\n" + str(playerIcon) + "\n\ncould not be found.\n" +
                "\n\nNo icon was set.")
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle="Warning")

    #creating background label
    background_label = tk.Label(windowCascade.root)
    background_label.pack()
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    #Loading default background
    if os.path.exists(backgroundFile) and os.path.isfile(backgroundFile):
        background_image = ImageTk.PhotoImage(Image.open(backgroundFile))
        background_label.configure(image=background_image)
        background_label.image = background_image
    else:
        text = ("File: \n\n" + str(backgroundFile) + "\n\ncould not be found.\n" +
                "\n\nThe background image was not loaded.")
        WindowDialog(text, Button1_Functionality=ButtonFunctionality("OK", None), windowTitle="Warning")


    button_style = ttk.Style()
    button_style.configure('Kim.TButton', foreground=fontColor.get())

    #creating buttons
    PausedButtonText = StringVar()
    PausedButtonText.set("Play")
    PauseButton = tk.Button(windowCascade.root,  #the first parameter is the widget
                       textvariable=PausedButtonText,  # the text on the button
                        height=allButtonsHeight,
                       width=allButtonsWidth, command=pause_music, #the width of the button, and the function which get called when clicking it
                        bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                       font=allButtonsFont.get()) #this is the font, size and type

    StopButton = tk.Button(windowCascade.root,  #the first parameter is the widget
                       text="Stop",  # the text on the button
                        height=allButtonsHeight,
                       width=allButtonsWidth, command=stop_music, #the width of the button, and the function which get called when clicking it
                        bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                        font=allButtonsFont.get()) #this is the font, size and type

    NextButton = tk.Button(windowCascade.root,  #the first parameter is the widget
                       text="Next",  # the text on the button
                        height=allButtonsHeight,
                       width=allButtonsWidth, command=next_song, #the width of the button, and the function which get called when clicking it
                           bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                       font=allButtonsFont.get()) #this is the font, size and type

    PreviousButton = tk.Button(windowCascade.root,  #the first parameter is the widget
                       text="Previous",  # the text on the button
                        height=allButtonsHeight,
                       width=allButtonsWidth, command=previous_song, #the width of the button, and the function which get called when clicking it
                               bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                       font=allButtonsFont.get()) #this is the font, size and type

    ShuffleButtonText = StringVar()
    if play_list.SHUFFLE:
        ShuffleButtonText.set("Shuffle On")
    else:
        ShuffleButtonText.set("Shuffle Off")

    ShuffleButton = tk.Button(windowCascade.root,  #the first parameter is the widget
                       textvariable=ShuffleButtonText,  # the text on the button
                        height=allButtonsHeight,
                       width=allButtonsWidth, command=shuffle, #the width of the button, and the function which get called when clicking it
                        bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                       font=allButtonsFont.get()) #this is the font, size and type

    RepeatButtonText = StringVar()
    if play_list.REPEAT == 0:
        RepeatButtonText.set("Repeat Off")
    elif play_list.REPEAT == 1:
        RepeatButtonText.set("Repeat All")
    elif play_list.REPEAT == 2:
        RepeatButtonText.set("Repeat One")
    elif play_list.REPEAT == 3:
        RepeatButtonText.set("Repeat None")

    RepeatButton = tk.Button(windowCascade.root,  #the first parameter is the widget
                       textvariable=RepeatButtonText,  # the text on the button
                        height=allButtonsHeight,
                       width=allButtonsWidth, command=repeat, #the width of the button, and the function which get called when clicking it
                        bg=SkinColor.get(), fg=fontColor.get(),  #bg is the background color of the button, fg is the text color
                       font=allButtonsFont.get()) #this is the font, size and type

    #Creating Volume:
    volume_scale_style = ttk.Style()
    volume_scale_style.theme_use('clam')
    volume_scale_style.configure('Vertical.TScale', background=SkinColor.get(), troughcolor=labelBackground.get(),
                          sliderlength =15, lightcolor=SkinColor.get(), darkcolor=SkinColor.get(),
                          slidertickness =40)

    VolumeScale = ttk.Scale(windowCascade.root, from_=100, to=0, orient=tk.VERTICAL,
                            length=(PauseButton.winfo_reqwidth() - 34), style="Vertical.TScale")
    VolumeScale.set(play_list.VolumeLevel*100)

    packPositionButton()

    labelPadX=2
    #Building the labels
    SongName = StringVar()
    SongName.set("Playing: ")

    labelPlayingFrame = tk.Frame(windowCascade.root, borderwidth=1, pady=1, padx=labelPadX, bg=labelBackground.get(), relief = tk.FLAT   , height=60)

    labelPlaying = tk.Label(labelPlayingFrame, textvariable=SongName, anchor=tk.W, compound=tk.CENTER, padx=labelPadX, bd=0, relief=tk.GROOVE \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())  # creating a label on the window

    textProgress = StringVar()

    if play_list.progressTime == "Ascending":
        textProgress.set("Time Elapsed: ")
    else:
        textProgress.set("Time Left: ")
    labelProgress = tk.Label(windowCascade.root, textvariable=textProgress, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())  # creating a label on the window

    textLength = StringVar()
    textLength.set("Length: ")
    labelLength = tk.Label(windowCascade.root, textvariable=textLength, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())  # creating a label on the window


    SongSize = StringVar()
    SongSize.set("Size: ")

    labelSize = tk.Label(windowCascade.root, textvariable=SongSize, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())  # creating a label on the window

    textStartTime = StringVar()
    textStartTime.set("Starts at: ")
    labelStartTime = tk.Label(windowCascade.root, textvariable=textStartTime, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())  # creating a label on the window


    textEndTime = StringVar()
    textEndTime.set("Ends at: ")
    labelEndTime = tk.Label(windowCascade.root, textvariable=textEndTime, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())  # creating a label on the window


    textFilesToPlay = StringVar()
    textFilesToPlay.set("Files: " + str(len(play_list.validFiles)))
    labelFilesToPlay = tk.Label(windowCascade.root, textvariable=textFilesToPlay, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())  # creating a label on the window


    textGenre = StringVar()
    textGenre.set("Genre: ")
    labelGenre = tk.Label(windowCascade.root, textvariable=textGenre, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())  # creating a label on the window


    textTotalPlayTime = StringVar()
    textTotalPlayTime.set("Total Length: ")
    labelTotalPlayTime = tk.Label(windowCascade.root, textvariable=textTotalPlayTime, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())  # creating a label on the window

    textSleepTimer = StringVar()
    textSleepTimer.set("Sleep Timer: NA")
    labelSleepTimer = tk.Label(windowCascade.root, textvariable=textSleepTimer, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())  # creating a label on the window

    textWakeTimer = StringVar()
    textWakeTimer.set("Wake Timer: NA")
    labelWakeTimer = tk.Label(windowCascade.root, textvariable=textWakeTimer, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())  # creating a label on the window

    textFadeIn = StringVar()
    textFadeIn.set("FadeIn: ")
    labelFadeIn = tk.Label(windowCascade.root, textvariable=textFadeIn, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())  # creating a label on the window

    textFadeOut = StringVar()
    textFadeOut.set("FadeOut: ")
    labelFadeOut = tk.Label(windowCascade.root, textvariable=textFadeOut, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())

    textMonoStereoMode = StringVar()
    textMonoStereoMode.set("Mode: ")
    labelMonoStereoMode = tk.Label(windowCascade.root, textvariable=textMonoStereoMode, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())

    textSampleRate = StringVar()
    textSampleRate.set("Sample Rate: ")
    labelSampleRate = tk.Label(windowCascade.root, textvariable=textSampleRate, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())

    textNofPlays = StringVar()
    textNofPlays.set("No. of Plays: ")
    labelNofPlays = tk.Label(windowCascade.root, textvariable=textNofPlays, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())

    textDanthologyMode = StringVar()
    textDanthologyMode.set("Danthology: OFF")
    labelDanthologyMode = tk.Label(windowCascade.root, textvariable=textDanthologyMode, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())

    textArtist = StringVar()
    textArtist.set("Artist: ")
    labelArtist = tk.Label(windowCascade.root, textvariable=textArtist, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())

    textAlbum = StringVar()
    textAlbum.set("Album: ")
    labelAlbum = tk.Label(windowCascade.root, textvariable=textAlbum, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())

    textTitle = StringVar()
    textTitle.set("Title: ")
    labelTitle = tk.Label(windowCascade.root, textvariable=textTitle, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())

    textYear = StringVar()
    textYear.set("Year: ")
    labelYear = tk.Label(windowCascade.root, textvariable=textYear, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())

    textSongListenedTime = StringVar()
    textSongListenedTime.set("Played time: ")
    labelSongListenedTime = tk.Label(windowCascade.root, textvariable=textSongListenedTime, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())

    textPlaylistListenedTime = StringVar()
    textPlaylistListenedTime.set("Total listening time: ")
    labelPlaylistListenedTime = tk.Label(windowCascade.root, textvariable=textPlaylistListenedTime, compound=tk.CENTER, padx=labelPadX \
                            , fg=labelTextColor, font=allButtonsFont.get(), background = labelBackground.get())
    packPositionLabels()


    #Creating a search form
    SearchForm = tk.Frame(windowCascade.root, borderwidth=1, pady=1, padx=1, bg=SkinColor.get(), relief=tk.SUNKEN)
    SearchFrame = tk.Frame(SearchForm, borderwidth=0, pady=0, padx=4, bg=SkinColor.get(), relief=tk.SUNKEN)
    labelSearch = tk.Label(SearchFrame, text="Search: ", padx=4, pady=0, anchor=tk.W, compound=tk.LEFT, width=7 \
                           , fg=fontColor.get(), font=allButtonsFont.get(), background=SkinColor.get(), borderwidth=0)

    ClearSearchButton = tk.Button(SearchForm,  # the first parameter is the widget
                                  text="Clear", borderwidth=2, padx=2, pady=0,  # the text on the button
                                  width=6, command=SearchBoxClear,
                                  # the width of the button, and the function which get called when clicking it
                                  bg=SkinColor.get(), fg=fontColor.get(),
                                  # bg is the background color of the button, fg is the text color
                                  font=allButtonsFont.get())  # this is the font, size and type

    searchValue = tk.Entry(SearchFrame, font=allButtonsFont.get(), width=45, relief=tk.GROOVE, \
                           borderwidth=1, fg=labelTextColor, background=labelBackground.get())

    #Creating a listbox
    ListboxFrame = tk.Frame(windowCascade.root, borderwidth=2, bg=SkinColor.get(), relief = tk.SUNKEN, padx=5, pady=5)

    #Creating style for scrollbar
    scroll_style = ttk.Style()
    scroll_style.theme_use('clam')
    scroll_style.configure("Vertical.TScrollbar", background=SkinColor.get(), bordercolor=SkinColor.get(),
                arrowcolor=fontColor.get(), relief=tk.GROOVE, arrowsize =20, troughcolor=labelBackground.get(),
                           activebackground = labelBackground.get())

    # Create a vertical scrollbar
    scroll = ttk.Scrollbar(ListboxFrame, orient='vertical')

    listbox = tk.Listbox(ListboxFrame, fg=fontColor.get(), font=allButtonsFont.get(), bg=SkinColor.get(), height=play_list.listboxNoRows,
                         width=70, relief=tk.GROOVE,
                         yscrollcommand=scroll.set, borderwidth=2, selectbackground = labelBackground.get(),
                         selectforeground = labelTextColor, activestyle="dotbox")

    #Search form should be equal in width with the listbox
    listbox["width"] = play_list.listboxWidth
    readjustSearchFormWidth()

    #Creating style for progressbar

    progress_style = ttk.Style()
    progress_style.theme_use('clam')
    progress_style.configure("Horizontal.TProgressbar", background=SkinColor.get(), bordercolor=labelTextColor,
                             troughcolor=labelBackground.get(), relief=tk.GROOVE)

    #Creating Progress bar
    progressBarLength = 290
    progress = Progressbar(orient=tk.HORIZONTAL, length=progressBarLength, mode=play_list.ProgressBarType, value=0, maximum = 100, \
                           style="Horizontal.TProgressbar") #using the same style

    #Setting the width of labelPlaying same as progressbar
    labelPlaying["wraplength"] = progressBarLength - 4 # - 4 becuase of the borders
    labelPlaying["width"] = int(progressBarLength / calculateLetterWidthPixels())-2
    labelPlayingFrame["width"] = progressBarLength

    #Creating RadioButton
    songRating = StringVar()
    songRating.set("0") # initialize

    radioButtonsDefaultColor = labelBackground.get()
    R1 = tk.Radiobutton(windowCascade.root,  variable=songRating, value=1, width=2, bg=radioButtonsDefaultColor, command=UpdateSongRating, fg = fontColor.get(), selectcolor="black", font=allButtonsFont.get(), borderwidth=0, relief=tk.GROOVE)
    R2 = tk.Radiobutton(windowCascade.root,  variable=songRating, value=2, width=2, bg=radioButtonsDefaultColor, command=UpdateSongRating, fg = fontColor.get(), selectcolor="black", font=allButtonsFont.get(), borderwidth=0, relief=tk.GROOVE)
    R3 = tk.Radiobutton(windowCascade.root,  variable=songRating, value=3, width=2, bg=radioButtonsDefaultColor, command=UpdateSongRating, fg = fontColor.get(), selectcolor="black", font=allButtonsFont.get(), borderwidth=0, relief=tk.GROOVE)
    R4 = tk.Radiobutton(windowCascade.root,  variable=songRating, value=4, width=2, bg=radioButtonsDefaultColor, command=UpdateSongRating, fg = fontColor.get(), selectcolor="black", font=allButtonsFont.get(), borderwidth=0, relief=tk.GROOVE)
    R5 = tk.Radiobutton(windowCascade.root,  variable=songRating, value=5, width=2, bg=radioButtonsDefaultColor, command=UpdateSongRating, fg = fontColor.get(), selectcolor="black", font=allButtonsFont.get(), borderwidth=0, relief=tk.GROOVE)
    labelSongRating = tk.Label(windowCascade.root, text="Rating: ", compound=tk.LEFT, padx=3, pady=3, \
                            fg=SkinColor.get(), font=allButtonsFont.get(),
                               background = radioButtonsDefaultColor, borderwidth=0, relief=tk.GROOVE)

    if labelBackground.get() == SkinColor.get() and play_list.skin_theme.unique_font_color == True:
        #if same sets of colors for buttons and labels we'll invert them in listbox selection to make
        #it look better
        labelSongRating["bg"] = labelBackground.get()
        labelSongRating["fg"] = labelTextColor
        R1["fg"] = labelTextColor
        R2["fg"] = labelTextColor
        R3["fg"] = labelTextColor
        R4["fg"] = labelTextColor
        R5["fg"] = labelTextColor
        listbox.configure(selectbackground = labelTextColor)
        listbox.configure(selectforeground = labelBackground.get())
        searchValue["bg"] = labelTextColor
        searchValue["fg"] = labelBackground.get()
        scroll_style.configure("Vertical.TScrollbar", bordercolor=labelTextColor)
        progress_style.configure("Horizontal.TProgressbar", background=labelTextColor,
                                 bordercolor=labelTextColor)
        volume_scale_style.configure('Vertical.TScale', background=labelTextColor, troughcolor=labelBackground.get(),
                                     lightcolor=labelTextColor, darkcolor=labelTextColor)

    packPositionListScrolOptionProgRadio()
    #windowCascade.root.wm_attributes('-transparentcolor', labelBackground.get())

    listener = pynput.keyboard.Listener(on_press=pressedHotkey)
    listener.start()

    # Setting up the scheduler
    scheduler = Scheduler(progressViewRealTime, 1, viewProgress)

    configurePlayer()

    #If file was opened using context menu
    if len(sys.argv) > 1:
        play_music() # this will play the track right after being loaded

    #Next time when the scheduler will run will call viewProgress function once within progressViewRealTime seconds
    scheduler.enter_mainloop()

    #Run the scheduler
    scheduler.run()

    windowCascade.root.mainloop() #loop through the window

    #join the listener with the main thread
    listener.join()