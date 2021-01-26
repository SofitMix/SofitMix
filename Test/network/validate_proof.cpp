#include <vector>
#include <iostream>
#include <string>
#include <iterator>
#include <algorithm>
#include "network.h"
#include <unistd.h>

#include <pthread.h>
#include <cassert>

using namespace std;

void *worker_routine (void *arg)
{
  zmq::context_t *context = (zmq::context_t *) arg;
  zmq::socket_t socket (*context, ZMQ_REP);
  socket.connect ("inproc://workers");

  Bin* signal;
  while(true)
  {
    vector<Bin*> reply;
    vector<Bin*> msgs;
    receive_Bin(socket,msgs);
    unsigned char tem[3];
    memcpy(tem,msgs[0]->data,msgs[0]->len);
    tem[2] = '\0';
    cout<<tem<<endl;
    sleep(2);


    signal = new Bin(22);
    memcpy(signal->data, "ZKproof is not correct", signal->len);
    reply.push_back(signal);
    send_Bin(socket,reply);
    
  }
    return (NULL);
}

int main ()
{
    //  Prepare our context and sockets
    zmq::context_t context (1);
    zmq::socket_t clients (context, ZMQ_ROUTER);
    clients.bind ("ipc:///tmp/ZeroMixer_sender");
    zmq::socket_t workers (context, ZMQ_DEALER);
    workers.bind ("inproc://workers");

    //  Launch pool of worker threads
    for (int thread_nbr = 0; thread_nbr != 10; thread_nbr++) {
        pthread_t worker;
        pthread_create (&worker, NULL, worker_routine, (void *) &context);
    }
    //  Connect work threads to client threads via a queue
    zmq::proxy (static_cast<void*>(clients),
                static_cast<void*>(workers),
                nullptr);
    return 0;
}
