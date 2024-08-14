from cx_Freeze import setup, Executable
import sys

# Dependencies are automatically detected, but it might miss some
build_exe_options = {
    "packages": ["os", "queue", "time", "threading", "psutil", "pystray", "PIL", "customtkinter"],
    "includes": [],
    "include_files": [("C:\\cpi\\barcode\\img\\logo.ico", "logo.ico"), ("log\\readerLog.txt", "log\\readerLog.txt")],
    "excludes": [],
    "optimize": 2,
    "build_exe": "build_exe"  # The directory where the build will be stored
}

# GUI applications require a different base on Windows (the default is for a console application)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="BarcodeReaderLogGUI",
    version="1.0",
    description="A GUI application for Barcode Reader Logs",
    options={"build_exe": build_exe_options},
    executables=[Executable("BarcodeReaderLogGUI.py", base=base, icon="logo.ico")]
)
