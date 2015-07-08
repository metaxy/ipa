#
# Ubuntu Dockerfile
#
# https://github.com/dockerfile/ubuntu
#

# Pull base image.
FROM ubuntu:14.04

# Install.
RUN \
  sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y build-essential && \
  apt-get install -y software-properties-common && \
  apt-get install -y byobu curl git htop man unzip vim wget && \
  apt-get install -y python3 python3-requests python3-flask-sqlalchemy && \
  rm -rf /var/lib/apt/lists/*

# Add files.
ADD src/server /root

# Set environment variables.
ENV HOME /root

# Define working directory.
WORKDIR /root
EXPOSE 8080
# Define default command.
RUN python3 /root/server.py --create-db -d
CMD ["python3","/root/server.py","-d"] 
