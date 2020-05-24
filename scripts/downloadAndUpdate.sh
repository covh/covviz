#!/bin/bash

git pull

source  ./py3science/bin/activate
cd src

python downloadAndUpdate.py | tee -a "../logs/$(date +%Y%m%d-%H%M)_downloadAndUpdate.log"


