from cx_Freeze import setup

# Dependencies are automatically detected, but they might need fine-tuning.
build_exe_options = {
    "includes": ["pynput.keyboard._win32", "pynput.mouse._win32"],
    'build_exe': './build_cxfreeze/'
}

setup(
    name="pyplay_mp3player_py310",
    version="4",
    description="PyPlay Mp3 Player",
    options={"build_exe": build_exe_options},
    executables=[{"script": "pyplay_mp3player_py310.py", "base": "gui",
    "icon" : "resources/headphone_red.ico"}],
)