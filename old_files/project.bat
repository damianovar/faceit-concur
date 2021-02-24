@echo off
title CONQUER

set mypath=%cd%

:start
    cls

REM Download python 3.8.4 to make sure user can make use of lambdas
set python_ver=384

REM Install pip if not already installed?
REM ------------- == --------------

REM Update pip till latest version
python -m pip install --upgrade pip

REM install all files in requirements.txt
pip3 install -r %mypath%\requirements.txt

REM Run script
python %mypath%\script.py

PAUSE