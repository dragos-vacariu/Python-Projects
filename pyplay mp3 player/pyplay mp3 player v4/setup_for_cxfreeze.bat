"python.exe" "./setup_for_cxfreeze.py" "build"
robocopy "resources" "build_cxfreeze/resources" /E
robocopy "backup" "build_cxfreeze/backup" /E
pause
