#!/bin/bash

LOGFILE="logs/$(date +%Y%m%d-%H%M)_initialize.log"

# make sure to work on the newest code
echo $(pwd) | tee -a $LOGFILE
git pull | tee -a $LOGFILE

# python dependencies, enter and log source folder
source  ./py3science/bin/activate
cd src
echo $(pwd) | tee -a ../$LOGFILE


# generate the 401*400/2 distances table
echo ... | tee -a ../$LOGFILE
echo python districtDistances.py | tee -a ../$LOGFILE
unbuffer python districtDistances.py | tee -a ../$LOGFILE


# generate all pages and pics
echo ... | tee -a ../$LOGFILE
echo python initializePlotsAndPages.py | tee -a ../$LOGFILE
unbuffer python initializePlotsAndPages.py | tee -a ../$LOGFILE


