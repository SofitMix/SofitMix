#ifndef NETWORK__h
#define NETWORK__h

#include "zmq.hpp"
#include <string>
#include <vector>
#include "utility.h"

void receive_multiparty(zmq::socket_t &socket, std::vector<std::string>& msgs);

void receive(zmq::socket_t &socket, std::string& msg);

void send(zmq::socket_t &socket, std::string msgs);

void send_multipart(zmq::socket_t &socket, std::vector<std::string>& msgs);

void receive_Bin(zmq::socket_t &socket, std::vector<Bin*>& msgs);

void send_Bin(zmq::socket_t &socket, std::vector<Bin*>& msgs);



#endif