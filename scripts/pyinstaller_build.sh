#! /bin/sh
#
# Build static binaries for Dit and Dit GUI
#

OLD_PWD=$PWD
cd ../dit/
pyinstaller --onefile dit-cli.py

if [ $? -ne 0 ]; then
	echo "Error building Dit CLI binary"
	exit 1
fi

pyinstaller --onefile dit-gui.py

if [ $? -ne 0 ]; then
	echo "Error building Dit CLI binary"
	exit 1
fi
