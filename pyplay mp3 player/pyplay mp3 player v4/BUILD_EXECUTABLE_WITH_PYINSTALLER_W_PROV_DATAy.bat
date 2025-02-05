@echo off REM comments will not be displayed in console/terminal window

"pyinstaller" --add-data "./data_for_pyinstaller/tkinterdnd2/tkdnd:." ^
--icon=./resources/headphone_red.ico -F --onedir --distpath="build_pyinstaller" --workpath="temp_pyinstaller" ^
--noconsole pyplay_mp3player_py310.py

robocopy "resources" "build_pyinstaller/pyplay_mp3player_py310/resources" /E
robocopy "backup" "build_pyinstaller/pyplay_mp3player_py310/backup" /E

@echo off
REM Pyinstaller can be used to compile the python script into an executable file. But usually that will also lead
REM to false positive threat reports by the antivirus SW. This happens because the Pyinstaller collapses all the needed libraries
REM and dependencies into a single file, which allows the executable to run independently of any other resource. 
REM This makes its signature similar to that of malicious softwares.

REM The option: --onedir should help workaround it a little. This should ensure we build one executable with .dll dependencies

pause