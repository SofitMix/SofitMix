#include "network.h"

void receive_multiparty(zmq::socket_t &socket, std::vector<std::string>& msgs){

  int64_t more = 1;
  size_t more_size = sizeof(more);
  zmq::message_t request;
  std::string item;
  
  while(more > 0){
    request.rebuild();
    socket.recv(&request);
    item = (char*)request.data();
    // Add to vec
    msgs.push_back(item);
    // Check to see if there's more
    socket.getsockopt(ZMQ_RCVMORE, &more, &more_size);
  }
}

void receive(zmq::socket_t &socket, std::string& msg){
  zmq::message_t request;

  request.rebuild();
  socket.recv(&request);
  msg = (char*)request.data();
}

void send(zmq::socket_t &socket, std::string msgs){

  zmq::message_t reply;
  int len;
  const char *tem; 

  len = msgs.size();
  reply.rebuild(len);
  tem = msgs.c_str();
  memcpy(reply.data(), tem, len);
  socket.send(reply, 0);
}


void send_multipart(zmq::socket_t &socket, std::vector<std::string>& msgs){

  zmq::message_t reply;
  int last_index = msgs.size() - 1;
  int len;
  const char *tem; 

  for(int i = 0; i < last_index; i++){
    len = msgs.at(i).size();
    tem = msgs.at(i).c_str();
    reply.rebuild(len);
    // strcpy(reply.data(), tem);
    memcpy(reply.data(), tem, len);
    socket.send(reply, ZMQ_SNDMORE);
  }
  len = msgs.at(last_index).size();
  reply.rebuild(len);
  tem = msgs.at(last_index).c_str();
  memcpy(reply.data(), tem, len);
  socket.send(reply, 0);
}

void receive_Bin(zmq::socket_t &socket, std::vector<Bin*>& msgs){

  int64_t more = 1;
  size_t more_size = sizeof(more);
  zmq::message_t request;

  Bin* item = NULL;
  while(more > 0){
    request.rebuild();

    socket.recv(&request);
    item = new Bin();
    item->len = request.size();
    item->data = (unsigned char *) malloc(item->len);
    memcpy(item->data, request.data(), request.size());

    // Add to vec
    msgs.push_back(item);

    // Check to see if there's more
    socket.getsockopt(ZMQ_RCVMORE, &more, &more_size);
  }
}

void send_Bin(zmq::socket_t &socket, std::vector<Bin*>& msgs){

  zmq::message_t reply;
  int last_index = msgs.size() - 1;

  for(int i = 0; i < last_index; i++){
    reply.rebuild(msgs.at(i)->len);
    memcpy(reply.data(), msgs.at(i)->data, msgs.at(i)->len);
    socket.send(reply, ZMQ_SNDMORE);
  }

  reply.rebuild(msgs.at(last_index)->len);
  memcpy(reply.data(), msgs.at(last_index)->data, msgs.at(last_index)->len);
  socket.send(reply, 0);
}
