#include <vector>
#include <iostream>
#include <string>
#include <iterator>
#include <algorithm>
#include <pthread.h>
#include <cassert>
#include "network.h"

using namespace std;




bool proof_validation(vector<Bin*> proof)
{
  return true;
}

// int main () {

//   // Prepare our context and socket
//   zmq::context_t local_context(1);
//   zmq::socket_t local_socket(local_context, ZMQ_REP);
//   local_socket.bind("tcp://127.0.0.1:5556");
//   vector<string> list_g{};  //检查g是否已存在,如果已存在，说明已经有一个receiver用同样的g要求建立交易。
//   Bin* signal;
//   zmq::context_t context_to_python(1);
//   zmq::socket_t socket_to_python(context_to_python, ZMQ_REQ);
//   socket_to_python.connect("ipc:///tmp/ZeroMixer_Mixer");

//   while(true)
//   {
//     vector<Bin*> reply;
//     vector<Bin*> msgs;
//     // ["ZKproof",sender.b,sender.g,sender.h_2,receiver.pubkey,pi]
//     receive_Bin(local_socket,msgs);
//     cout<<"g is: ";
//     print_hex(msgs[2]->len,msgs[2]->data);
//     vector<Bin*> proof_info = msgs;
//     proof_info.erase(proof_info.begin()+4);
//     proof_info.erase(proof_info.begin());
//     std::string *g = byteToHexStr(msgs[2]->data,msgs[2]->len);

//     unsigned char *temp = (unsigned char*) malloc(msgs[0]->len+1);
//     memcpy(temp, msgs[0]->data, msgs[0]->len);
//     temp[msgs[0]->len] = '\0';
//     if (!strcmp((char*)temp,"ZK_proof") && ((!list_g.empty() && find(list_g.begin(),list_g.end(),*g)==list_g.end())||list_g.empty())&& proof_validation(proof_info))
//     {     
//       cout<<"enter here"<<endl;
//       list_g.push_back(*g); 
//       signal = new Bin(14);
//       memcpy(signal->data, "correct Mproof", signal->len);
//       //correct Mproof, b, g, h_2, receiver.pubkey
//       vector<Bin*> python_list= {signal,msgs[1],msgs[2],msgs[3],msgs[4]};
//       send_Bin(socket_to_python,python_list);

//       cout<<1<<endl;
//       receive_Bin(socket_to_python,reply);
//       cout<<2<<endl;
//       cout<<"reply length is: "<<reply.size()<<endl;
//       // reply = [funding_txid, block_count, mixer_pubkey, LOCKTIME] or "TX already redeemed by sender"
//       send_Bin(local_socket,reply); //to receiver

      
//     }
//     else if (strcmp((char*)temp,"ZK_proof"))
//     {
//       signal = new Bin(23);
//       memcpy(signal->data, "the format is not right", signal->len);
//       reply.push_back(signal);
//       send_Bin(local_socket,reply);
//     }
//     else if (!list_g.empty() && find(list_g.begin(),list_g.end(),*g)!=list_g.end())
//     {
//       signal = new Bin(42);
//       memcpy(signal->data, "TX is already redeemed by another receiver", signal->len);
//       reply.push_back(signal);
//       send_Bin(local_socket,reply);
//     }
//     else
//     {
//       signal = new Bin(22);
//       memcpy(signal->data, "ZKproof is not correct", signal->len);
//       reply.push_back(signal);
//       send_Bin(local_socket,reply);
//     }
//   }

//   return 0;
// }


void *worker_routine (void *arg)
{
  zmq::context_t *context = (zmq::context_t *) arg;
  zmq::socket_t socket (*context, ZMQ_REP);
  socket.connect ("inproc://workers");

  vector<string> list_g{};  //检查g是否已存在,如果已存在，说明已经有一个receiver用同样的g要求建立交易。
  Bin* signal;
  zmq::context_t context_to_python(1);
  zmq::socket_t socket_to_python(context_to_python, ZMQ_REQ);
  socket_to_python.connect("ipc:///tmp/ZeroMixer_Mixer");

  while(true)
  {
    vector<Bin*> reply;
    vector<Bin*> msgs;
    // ["ZKproof",sender.b,sender.g,sender.h_2,receiver.pubkey,pi]
    receive_Bin(socket,msgs);
    cout<<"g is: ";
    print_hex(msgs[2]->len,msgs[2]->data);
    vector<Bin*> proof_info = msgs;
    proof_info.erase(proof_info.begin()+4);
    proof_info.erase(proof_info.begin());
    std::string *g = byteToHexStr(msgs[2]->data,msgs[2]->len);

    unsigned char *temp = (unsigned char*) malloc(msgs[0]->len+1);
    memcpy(temp, msgs[0]->data, msgs[0]->len);
    temp[msgs[0]->len] = '\0';
    if (!strcmp((char*)temp,"ZK_proof") && ((!list_g.empty() && find(list_g.begin(),list_g.end(),*g)==list_g.end())||list_g.empty())&& proof_validation(proof_info))
    {     
      cout<<"enter here"<<endl;
      list_g.push_back(*g); 
      signal = new Bin(14);
      memcpy(signal->data, "correct Mproof", signal->len);
      //correct Mproof, b, g, h_2, receiver.pubkey
      vector<Bin*> python_list= {signal,msgs[1],msgs[2],msgs[3],msgs[4]};
      send_Bin(socket_to_python,python_list);

      cout<<1<<endl;
      receive_Bin(socket_to_python,reply);
      cout<<2<<endl;
      cout<<"reply length is: "<<reply.size()<<endl;
      // reply = [funding_txid, block_count, mixer_pubkey, LOCKTIME] or "TX already redeemed by sender"
      send_Bin(socket,reply); //to receiver

      
    }
    else if (strcmp((char*)temp,"ZK_proof"))
    {
      signal = new Bin(23);
      memcpy(signal->data, "the format is not right", signal->len);
      reply.push_back(signal);
      send_Bin(socket,reply);
    }
    else if (!list_g.empty() && find(list_g.begin(),list_g.end(),*g)!=list_g.end())
    {
      signal = new Bin(42);
      memcpy(signal->data, "TX is already redeemed by another receiver", signal->len);
      reply.push_back(signal);
      send_Bin(socket,reply);
    }
    else
    {
      signal = new Bin(22);
      memcpy(signal->data, "ZKproof is not correct", signal->len);
      reply.push_back(signal);
      send_Bin(socket,reply);
    }
  }
    return (NULL);
}

int main ()
{
    //  Prepare our context and sockets
    zmq::context_t context (1);
    zmq::socket_t clients (context, ZMQ_ROUTER);
    clients.bind ("tcp://127.0.0.1:5556");
    zmq::socket_t workers (context, ZMQ_DEALER);
    workers.bind ("inproc://workers");

    //  Launch pool of worker threads
    for (int thread_nbr = 0; thread_nbr != 400; thread_nbr++) {
        pthread_t worker;
        pthread_create (&worker, NULL, worker_routine, (void *) &context);
    }
    //  Connect work threads to client threads via a queue
    zmq::proxy (static_cast<void*>(clients),
                static_cast<void*>(workers),
                nullptr);
    return 0;
}