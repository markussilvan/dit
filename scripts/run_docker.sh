#! /bin/sh
# Run this script from the project root directory

if [ ! -d ".git" ]; then
	echo "Script not run from the project root directory"
	exit 1
fi

docker run -it -v $(pwd)/dit/:/home/external/dit/ dit:latest
