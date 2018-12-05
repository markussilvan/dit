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

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y expect

# copy a script to update external volume mappings to a local copy
#
# in addition two volume mappings are needed
#   - source tree should be mapped to /home/external/dit/
#   - testenv directory should be mapped to /home/external/testenv/
COPY testenv/update_externals.sh /home/app

WORKDIR /home/app/

RUN ln -s /home/app/dit/dit-cli.py /bin/dit
