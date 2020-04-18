#!/bin/bash

timeout 7 python -B playground.py &
sleep 5
xwd -name "pyglwidgets" | convert xwd:- "$1"
