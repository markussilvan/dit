#! /bin/sh
# Start an existing Docker container for testing Dit

CONTAINER_ID=`docker ps --latest --quiet`

docker start -i ${CONTAINER_ID}
