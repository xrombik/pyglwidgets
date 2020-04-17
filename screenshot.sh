#!/bin/bash

xwd -name "pyglwidgets" | convert xwd:- "$1"
