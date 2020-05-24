#!/bin/bash

LOGFILE="logs/$(date +%Y%m%d-%H%M)_initialize.log"

# make sure to work on the newest code
echo $(pwd) | tee -a $LOGFILE
git pull | tee -a $LOGFILE

# python dependencies, enter and log source folder
source  ./py3science/bin/activate
cd src
echo $(pwd) | tee -a ../$LOGFILE

# generate all pages and pics
unbuffer python initializePlotsAndPages.py | tee -a ../$LOGFILE


