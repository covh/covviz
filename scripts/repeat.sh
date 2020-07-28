#!/bin/bash

####   nohup ./repeat.sh >> nohup.out 2>&1 &

echo 
echo "###############################################################"
echo "# started new"
echo "###############################################################"
date
echo
echo sleep until the new CSV is there at approx 2am ...
echo sleep  14400
sleep 14400
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
  echo sleep 6700
  sleep 6700
  echo slept.


  echo repeated night round, at
  date
  echo
  cd /root/covh/covviz; scripts/downloadAndUpdate.sh

  echo
  echo now sleep a bit less than 12 hours and catch the afternoon data
  echo sleep 42700
  sleep 42700
  echo slept.
  echo

  echo afternoon round, at
  date
  echo
  cd /root/covh/covviz; scripts/downloadAndUpdate.sh

  echo
  echo now sleep a bit less than 10 hours and do the next night
  echo sleep 35500
  sleep 35500
  echo slept.
  echo

done
