#!/bin/bash
set -e

# Sets the missing dependencies if necessary
# PACKS - contains a list of all dependencies used.
# Only for *.deb operating systems (Debian, Ubuntu, Mint, etc.).
PACKS=("python-gtk2" "libgtkglext1" "python-opengl" "python-gtkglext1" "python-pip" "imagemagick")

sudo apt-get autoremove -f -y
sudo apt-get update -y
sudo apt-get upgrade -y

for PACK in "${PACKS[@]}"
do
  echo -n "Check for package availability \"$PACK\" ... "
  dpkg -s "${PACK}" > /dev/null
  if [[ $? -ne 0 ]] ; then
    echo "\"$PACK\" hasn't been found, and will be installed."
    sudo apt-get install "${PACK}" -y
  else
    echo " found."
  fi
done
