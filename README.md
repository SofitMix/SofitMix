
Refer https://samsclass.info/141/proj/pBitc1.htm and https://medium.com/@cavapoo2/setting-up-bitcoin-core-on-ubuntu-16-04-679d98a393bb to configure bitcoin core
Compiling Bitcoin Core from Source
Execute these commands to clone the Bitcoin repository, and to see the versions available.

    git clone https://github.com/bitcoin/bitcoin.git

    cd bitcoin

    git tag

 Execute these commands to clone the latest version and see compile-time options.

    git checkout v0.19.1rc2

    ./autogen.sh

I get some errors from this, mainly about Libtool library used but ‘LIBTOOL’ is undefined. Try this:

    sudo apt-get install autoconf libtool libssl-dev libboost-all-dev libminiupnpc-dev libevent-dev libncurses5-dev -y

Execute these commands:

    ./configure --with-incompatible-bdb

This time i get an error libdb_cxx headers missing, Bitcoin Core requires this library for wallet functionality.

Try this:

sudo add-apt-repository ppa:bitcoin/bitcoin
sudo apt-get update
sudo apt-get install libdb4.8-dev libdb4.8++-dev

Now try configure again (./configure). This time i get this error :

error: No working boost sleep implementation found.

try this:

sudo apt-get install libboost-system-dev libboost-filesystem-dev libboost-chrono-dev libboost-program-options-dev libboost-test-dev libboost-thread-dev

Now try to configure again (./configure). This time i get this error:

error: libevent not found

try this:

sudo apt-get install libevent-dev

This time ./configure should work.

    make

The compiling takes about 10-20 minutes. It also requires at least 2 GB of RAM.

Execute these commands to install the bitcoin core software, and to check the installation location:

    sudo make install

    which bitcoind

    which bitcoin-cli

Creating a Configuration File
Execute these commands:

    cd
    mkdir .bitcoin
    nano .bitcoin/bitcoin.conf

Paste in these lines, replacing the password with something unique: 
rpcuser=bitcoinrpc
rpcpassword=7bLjxV1CKhNJmdxTUMxTpF4vEemWCp49kMX9CwvZabYi
rpcworkqueue=1000
rpctimeout=3000
rpcservertimeout=3000
rpcclienttimeout=3000

synchronize testnet:
bitcoind -testent

Wait until finishing testnet synchronization. Execute this command to start the Bitcoin daemon:

bitcoind -regtest -daemon

Set wallet:
bitcoin-cli -testnet encryptwallet @passward
bitcoin-cli -testnet walletpassphrase @passward 3600

python dependencies: pip3 install -r requirements.txt

For ubuntu, you can install the dependemcies by running:
./ubuntu_setup.sh

Run the program:

make

Mixer:
./Mixer/mixer_server.py
./Mixer/mixer_tx_server.py
./Mixer/bin/validate_proof

Receiver:
./Receiver/receiver_server.py

Sender:
./Sender/bin/ZK
./Sender/sender_client.py
# Mulit_Client
