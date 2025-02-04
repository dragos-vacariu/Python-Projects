"./Python310\Scripts/pyinstaller.exe" --add-data "./Python310/Lib/site-packages/tkinterdnd2/tkdnd:." ^
 --icon=./resources/headphone_red.ico -F ^
--noconsole pyplay_mp3player_py310.py

REM Pyinstaller can be used to compile the python script into an executable file. But usually that will also lead ^
to false positive threat reports by the antivirus SW. This happens because the Pyinstaller collapses all the needed libraries ^
and dependencies into a single file, which allows the executable to run independently of any other resource. This makes its signature ^
similar to that of malicious softwares.

pause