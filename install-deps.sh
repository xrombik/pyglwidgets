#!/bin/bash
set -e

# Sets the missing dependencies if necessary
# PACKS - contains a list of all dependencies used.
# Only for *.deb operating systems (Debian, Ubuntu, Mint, etc.).
PACKS=("python-gtk2" "libgtkglext1" "python-opengl" "python-gtkglext1" "python-pip")

apt-get autoremove -f -y
apt-get update -y
apt-get upgrade -y

for PACK in "${PACKS[@]}"
do
	echo -n "Check for package availability \"$PACK\" ... "
	dpkg -s $PACK > /dev/null
	if [ $? -ne 0 ]; then
		echo "\"$PACK\" hasn't been found, and will be installed."
		apt-get install $PACK -y
	else
		echo " found."
	fi
done

pip install --upgrade pip
pip install setuptools
pip install freetype-py
pip install typing
