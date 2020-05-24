#!/bin/bash

LOGFILE="logs/$(date +%Y%m%d-%H%M)_downloadAndUpdate.log"

# make sure to work on the newest code
git pull | tee -a $LOGFILE

# merge with newer site data possibly generated on different machine 
cd ../cov19de
echo $(pwd) | tee -a ../covviz/$LOGFILE
git pull | tee -a ../covviz/$LOGFILE

# come back to code repo
cd ../covviz
echo $(pwd) | tee -a $LOGFILE

# python dependencies, enter and log source folder
source  ./py3science/bin/activate
cd src
echo $(pwd) | tee -a ../$LOGFILE

# the whole shebang
python downloadAndUpdate.py | tee -a ../$LOGFILE


