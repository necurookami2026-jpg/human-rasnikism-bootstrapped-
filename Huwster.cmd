@echo off
cd /d "%~dp0"
py -3 -m madrigal_lab.app gui
if errorlevel 1 pause
