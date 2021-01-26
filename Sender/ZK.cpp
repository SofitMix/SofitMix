#include <iostream>
#include <openssl/sha.h>
#include "network.h"
#include "utility.h"
#include <pthread.h>
#include <cassert>
// #include <iomanip>
// #include <sstream>
using namespace std;


void parse_msg(string msg, Bin &a, Bin &b, Bin &h_1, Bin &h_2, Bin &g, Bin &root, vector<Bin> &path)
{ 
    // cout<<msg<<endl;  
    int Hash_length = SHA256_DIGEST_LENGTH;
    int Hash_g_length = SHA_DIGEST_LENGTH;  
    neb::CJsonObject json_msg(msg);

    // [sender.a,sender.b,sender.h_1.hex(),sender.h_2.hex(),sender.g.hex(),root.hex(),proof]
    string item;
    json_msg.Get(0,item);
    a.data = (unsigned char *) tmalloc(item.length());
    memcpy(a.data,item.c_str(),item.length()); 
    a.len = item.length();
    cout<<a.data<<endl;

    json_msg.Get(1,item);
    b.data = (unsigned char *) tmalloc(item.length());
    memcpy(b.data,item.c_str(),item.length());
    b.len = item.length();
    cout<<b.data<<endl;

    json_msg.Get(2,item);
    unsigned char *hex_str;
    hex_str = (unsigned char *) tmalloc(item.length());
    memcpy(hex_str,item.c_str(),item.length()); 
    h_1.data = (unsigned char *) tmalloc(Hash_length); 
    h_1.len = Hash_length;
    HexStrToByte(hex_str, h_1.data, h_1.len*2); //将hex转为bytes存到h_1中
    //打印
    // printBytes(h_1.data,h_1.len);
    cout<<hex_str<<endl;

    json_msg.Get(3,item);
    hex_str = (unsigned char *) tmalloc(item.length());
    memcpy(hex_str,item.c_str(),item.length());
    h_2.data = (unsigned char *) tmalloc(Hash_length); 
    h_2.len = Hash_length;
    HexStrToByte(hex_str, h_2.data, h_2.len*2);
    // printBytes(h_2.data,h_2.len);
    cout<<hex_str<<endl;

    json_msg.Get(4,item);
    hex_str = (unsigned char *) tmalloc(item.length());
    memcpy(hex_str,item.c_str(),item.length()); 
    g.data = (unsigned char *) tmalloc(Hash_g_length); 
    g.len = Hash_g_length;
    HexStrToByte(hex_str, g.data, g.len*2);
    // printBytes(g.data,Hash_g_length);
    cout<<hex_str<<endl;

    json_msg.Get(5,item);
    hex_str = (unsigned char *) tmalloc(item.length());
    memcpy(hex_str,item.c_str(),item.length()); 
    root.data = (unsigned char *) tmalloc(Hash_length); 
    root.len = Hash_length;
    HexStrToByte(hex_str, root.data, root.len*2);
    // printBytes(root.data,root.len);
    cout<<hex_str<<endl;

    for(int i = 0; i<json_msg[6].GetArraySize(); i++)
    {   
        Bin bin;
        string key;
        string value;
        neb::CJsonObject dict;
        json_msg[6].Get(i,dict);
        dict.GetKey(key);
        int ikey=atoi(key.c_str());
        bin.flag = ikey;
        dict.Get(key,value);
        hex_str = (unsigned char *) tmalloc(value.length());
        memcpy(hex_str,value.c_str(),value.length()); 
        bin.data = (unsigned char *) tmalloc(Hash_length); 
        bin.len = Hash_length;
        HexStrToByte(hex_str, bin.data, bin.len*2);
        // cout<<hex_str<<endl; 
        // printBytes(bin.data,bin.len);
        path.push_back(bin);

    }
    //test 正确
    /*
    cout<<"test"<<endl;
    unsigned char buf[Hash_length];
    SHA256(a.data, a.len, buf);
    printHex(buf,Hash_length);
    printBytes(buf,Hash_length);

    SHA256(b.data, b.len, buf);
    printHex(buf,Hash_length);
    printBytes(buf,Hash_length);

    unsigned char gbuf[Hash_g_length];
    SHA1(a.data, a.len, gbuf);
    printHex(gbuf,Hash_g_length);
    printBytes(gbuf,Hash_g_length);

    Bin ab;
    ab.data = (unsigned char *) tmalloc (a.len+b.len);
    ab.len = a.len + b.len;
    for(int i = 0; i<a.len; i++)
    {
      ab.data[i] = a.data[i];
    }
    for (int j =0; j<b.len; j++)
    {
      ab.data[a.len+j] = b.data[j];
    }
    printBytes(ab.data,ab.len);
    SHA256(ab.data, ab.len, buf);
    printHex(buf,Hash_length);
    printBytes(buf,Hash_length);
    */
}
string* byteToHexStr(unsigned char byte_arr[], int arr_len)
{  
  string* hexstr=new string(); 
  for (int i=0;i<arr_len;i++)
  {
    char hex1;
    char hex2;
    int value=byte_arr[i];
    int S=value/16; 
    int Y=value % 16;
    if (S>=0&&S<=9)
    hex1=(char)(48+S);
    else 
    hex1=(char)(55+S);
    if (Y>=0&&Y<=9)
    hex2=(char)(48+Y);
    else
    hex2=(char)(55+Y);
    *hexstr=*hexstr+hex1+hex2; 
  }
 
return hexstr;
}

void zkproof(vector<Bin*> elements, Bin* &pi)
{
  pi = new Bin(4);
  memcpy(pi->data, "True", pi->len);

  cout<<pi<<endl;

}
// int main () {
//     // msg = [sender.a,sender.b,sender.h_1,sender.h_2,sender.g,root,proof]
//   // Prepare our context and socket
//   zmq::context_t context(1);
//   zmq::socket_t socket(context, ZMQ_REP);
//   socket.bind("ipc:///tmp/ZeroMixer_sender");


//   while(true)
//   {
//     string msg;
//     receive(socket,msg);

//     Bin a, b, h_1, h_2, g, root;
//     vector<Bin> path;
//     parse_msg(msg, a, b, h_1, h_2, g, root, path);


//   //   //here is zero knowledge proof
//   //   /*
//   //   string pi;
//   //   zkproof(msg,pi);
//   //   send(socket,pi); pi应是unsigned char*,
//   //   

//     string reply="True";
//     // vector<string> re = {charArray_to_String(path[0].data,path[0].len),charArray_to_String(path[1].data,path[1].len),charArray_to_String(path[2].data,path[2].len),charArray_to_String(path[3].data,path[3].len)};
//     //send(socket,charArray_to_String(pi.data,pi.len))
//     send(socket,msg);

//   }

//   return 0;
// }


void *worker_routine (void *arg)
{
  zmq::context_t *context = (zmq::context_t *) arg;
  zmq::socket_t socket (*context, ZMQ_REP);
  socket.connect ("inproc://workers");

  while(true)
  {
    string msg;
    receive(socket,msg);

    Bin a, b, h_1, h_2, g, root;
    vector<Bin> path;
    parse_msg(msg, a, b, h_1, h_2, g, root, path);

    //here is zero knowledge proof
    
    vector<Bin*> msgs;
    msgs.push_back(&a);
    msgs.push_back(&b);
    msgs.push_back(&h_1);
    msgs.push_back(&h_2);
    msgs.push_back(&g);
    msgs.push_back(&root);
    Bin* pi;
    cout<<pi<<endl;
    zkproof(msgs,pi);
    cout<<pi<<endl;
    // cout<<pi->data<<endl;
    vector<Bin*> reply;
    reply.push_back(pi);
    // cout<<"enter vector"<<endl;
    // for(auto i:reply)
    // {
    //   cout<<i->data<<endl;
    // }
    cout<<"send Bin"<<endl;
    send_Bin(socket,reply);
    cout<<"end"<<endl; 

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