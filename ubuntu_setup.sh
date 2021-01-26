#!/bin/bash

# Configure Ubuntu

# Build essentials
sudo apt-get update
sudo apt-get install libzmq3-dev
sudo apt-get install python3-pip

# Install ZMQ
# git clone https://github.com/zeromq/libzmq
# CPPFLAGS=-DZMQ_MAKE_VALGRIND_HAPPY
# cd libzmq
# ./autogen.sh
# ./configure
# make -j 4
# make check
# make install
# sudo ldconfig
# cd ..
# rm -rf libzmq/

mkdir download
cd download
wget https://github.com/jedisct1/libsodium/releases/download/1.0.3/libsodium-1.0.3.tar.gz
tar -zxvf libsodium-1.0.3.tar.gz
cd libsodium-1.0.3
./configure
make
sudo make install
cd ..
wget https://archive.org/download/zeromq_4.0.3/zeromq-4.0.3.tar.gz
tar -zxvf zeromq-4.0.3.tar.gz
cd zeromq-4.0.3
./configure --without-libsodium
make
sudo make install
sudo ldconfig
cd ..
cd ..
rm -rf download/
#Install 


# Install python dependencies
pip3 install -r requirements.txt

# sudo apt-get install libzmq-dev

#Install jsoncpp
sudo apt-get install libjsoncpp-dev

sudo ln -s /usr/include/jsoncpp/json/ /usr/include/json

#Terminator tool:
sudo apt-get install terminator
