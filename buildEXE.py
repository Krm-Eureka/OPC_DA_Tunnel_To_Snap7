import subprocess

subprocess.call([
    "pyinstaller",
    "--onefile",
    "--windowed",
    "--hidden-import=win32timezone",
    "--hidden-import=pythoncom",
    "--collect-all", "win32com",
    "main.py"
])
