#!/bin/bash

n=0
until [ "$n" -ge 8 ]
do
   python ~/pyobd-pi/obd_recorder.py && break  # substitute your command here
   n=$((n+1)) 
   sleep 15
done