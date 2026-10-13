@echo off
cd /d "%~dp0"
py -3 download_images.py
if errorlevel 1 python download_images.py
