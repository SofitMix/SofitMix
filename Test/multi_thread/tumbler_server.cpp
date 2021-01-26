#include <vector>
#include <iostream>
#include <string>
#include <unistd.h>
#include <thread>
#include "zmq.hpp"


using namespace std;
/*
//version 1: use vector<char*>
void receive(zmq::socket_t &socket, vector<char*>& msgs){

  int64_t more = 1;
  size_t more_size = sizeof(more);
  zmq::message_t request;
  int len;
  char * data;
  
  
  while(more > 0){
    request.rebuild();
    socket.recv(&request);

    len = request.size();
    data = (char *) malloc(len);
    memcpy(data, request.data(), request.size());
    // Add to vec
    msgs.push_back(data);
    // Check to see if there's more
    socket.getsockopt(ZMQ_RCVMORE, &more, &more_size);
  }
}
int main () {

  // Prepare our context and socket
  zmq::context_t context(1);
  zmq::socket_t socket(context, ZMQ_REP);
  socket.bind("ipc:///tmp/ZeroMixer_tx");
  vector<char*> requests;
  receive(socket,requests);
  vector<string> message;
  //convert to string
  for (auto info : requests)
  {
    message.push_back(info);
    cout<<info<<endl;
  }

  return 0;
}
*/


// version 2: use vector<string>
void receive(zmq::socket_t &socket, vector<string>& msgs){

  int64_t more = 1;
  size_t more_size = sizeof(more);
  zmq::message_t request;
  string item;
  
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

void send(zmq::socket_t &socket, vector<string>& msgs){

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

void p(int i)
{
  sleep(3);
  cout<<i<<endl;
}

int main () {

  // Prepare our context and socket
  zmq::context_t context(2);
  zmq::socket_t socket(context, ZMQ_REP);
  socket.bind("ipc:///tmp/ZeroMixer_tx");
  int i =0;
  while(true)
  {
    vector<string> s;

    // thread t1(receive,ref(socket),ref(s));
    receive(socket,s);
    for (auto info : s)
    {
      cout<<info<<endl;
    }
    
    thread t1(p,i);

    vector<string> reply={"hello","client"};
    send(socket,reply);
    // i = 1;

    t1.detach(); 

  }
  return 0;
}
