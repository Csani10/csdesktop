#!/bin/bash

read -p "Delete configs (Y,n): " configsdel
configsdel=${configsdel:-Y}

if [ "$configsdel" = "y" ]; then
rm -rf $HOME/.config/csdesktop
fi

bin="/usr/local/bin"

sudo rm $bin/csvol
sudo rm $bin/csfm
sudo rm $bin/cspanel
sudo rm $bin/csedit