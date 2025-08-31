@echo off
REM Navigate to the folder where this .bat file is located
cd /d "%~dp0"

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Run the Python file
python Main.py

REM Deactivate the virtual environment
deactivate

REM Keep the command prompt open to see output
pause
