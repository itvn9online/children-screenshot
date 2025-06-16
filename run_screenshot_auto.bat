@echo off
REM Batch file to run screenshot_auto.py at startup
REM Update the path to python.exe if needed

set PYTHON_PATH=python
set SCRIPT_PATH=D:\children-screenshot\screenshot_auto.py

%PYTHON_PATH% "%SCRIPT_PATH%"
