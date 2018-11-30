# Dockerfile describing the enviroment for testing Dit

FROM ubuntu
MAINTAINER Markus Silván "markus.silvan@iki.fi"

# install required tools
RUN apt-get update
RUN apt-get install -y python3 python3-pip

# copy software
COPY dit /home/dit
COPY requirements.txt /home/

#TODO: this is temporary while dit init doesn't work
COPY .dit-config /home/
COPY issues /home/issues



WORKDIR /home/

# install Dit requirements
RUN pip3 install -r requirements.txt

WORKDIR /home/dit
