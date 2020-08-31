#!/bin/bash

####
####   nohup ./repeat.sh >> nohup.out 2>&1 &
####
####   ps aux | grep "sleep\|repeat" | grep -v grep
####

echo 
echo "###############################################################"
echo "# started new"
echo "###############################################################"
date
echo
echo sleep until the new CSV is there at approx 1am ...
echo sleep 52000
sleep 52000
echo slept.

echo
echo now loop:

while true
do
  echo doing next round, at
  date
  echo
  cd /root/covh/covviz; scripts/downloadAndUpdate.sh

  echo 
  echo now sleep a bit less than 2 hours and just do it again
  echo sleep 7000
  sleep 7000
  echo slept.


  echo repeated night round, at
  date
  echo
  cd /root/covh/covviz; scripts/downloadAndUpdate.sh

  echo
  echo now sleep a bit less than 12 hours and catch the afternoon data
  echo sleep 42000
  sleep 42000
  echo slept.
  echo

  echo afternoon round, at
  date
  echo
  cd /root/covh/covviz; scripts/downloadAndUpdate.sh

  echo
  echo now sleep a bit more than 10 hours and do the next night
  echo sleep 37000
  sleep 37000
  echo slept.
  echo

done

