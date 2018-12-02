# Dockerfile describing the enviroment for testing Dit

FROM ubuntu
MAINTAINER Markus Silván "markus.silvan@iki.fi"

# install required tools
RUN apt-get update
RUN apt-get install -y python3 python3-pip

RUN mkdir -p /home/app
WORKDIR /home/app

# copy requirements file for pip to use
COPY requirements.txt /home/app

# install Dit requirements
RUN pip3 install -r requirements.txt

#TODO: this is temporary while dit init doesn't work
COPY .dit-config /home/app
#TODO: copy test data from unit test instead of real issues?
#      or make a script to genereate the test data
COPY issues /home/app/issues

# copy script to update /home/app/dit from external source tree
# the software itself should be mapped to a read-only volume at /home/external/dit/
COPY virtual/update_source_from_external.sh /home/app

WORKDIR /home/app/
