#!/bin/bash

####   nohup ./repeat.sh >> nohup.out 2>&1 &

echo
echo until the new CSV is there at approx 2am ...
echo sleep 18000
sleep 18000
echo
echo now loop:

while true
do
  echo next round, at
  date
  echo

  cd /root/covh/covviz; scripts/downloadAndUpdate.sh

  echo
  echo now sleep 86000
  sleep 86000
  echo slept.
  echo
done
