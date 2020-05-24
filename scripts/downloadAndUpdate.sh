#!/bin/bash

# exit when any command fails
set -e
# keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# echo an error message before exiting
trap 'echo; echo "\"${last_command}\" command filed with exit code $?."' EXIT


LOGFILE="logs/$(date +%Y%m%d-%H%M)_downloadAndUpdate.log"

# make sure to work on the newest code
git pull | tee -a $LOGFILE

# merge with newer site data possibly generated on different machine 
# remaining problem: plots contain the time so they will always be rewritten.
# (Perhaps also differing matplotlib different PNG binaries?)
# --> Either do NOT often switch machines ... or remove the time from the plots?
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
# remove the unbuffer command OR install unbuffer for this to work:    sudo apt install expect
unbuffer python downloadAndUpdate.py | tee -a ../$LOGFILE

exit done.


