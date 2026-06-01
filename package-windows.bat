@echo off
setlocal

py -m pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1

py -m PyInstaller --onefile --windowed --name OneLongDay game.py
if errorlevel 1 exit /b 1

echo Windows build complete:
echo   dist\OneLongDay.exe
