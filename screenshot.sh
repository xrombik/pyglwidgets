#!/bin/bash

timeout 7 python -B playground.py &
sleep 5
xwd -name "pyglwidgets demo" | convert xwd:- "$1"
