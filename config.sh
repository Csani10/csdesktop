#!/bin/bash

mkdir -p $HOME/.config/csdesktop
cp configs/* $HOME/.config/csdesktop

mkdir -p $HOME/.local/share/applications

cp desktop-files/csfm.desktop $HOME/.local/share/applications/
cp desktop-files/csedit.desktop $HOME/.local/share/applications/
