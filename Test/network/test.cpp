#include <vector>
#include "network.h"

using namespace std;

int main()
{

	Bin* raw_tx;
	Bin* temp;
	vector<Bin*> reply;
	vector<Bin*> requests;

	zmq::context_t context(1);
	zmq::socket_t socket(context, ZMQ_REP);
	socket.bind("ipc:///tmp/ZeroMixer_sender");

	receive(socket, reply);

	raw_tx->len = reply.at(0)->len;
	raw_tx->data = reply.at(0)->data;
	reply.at(0)->len = 0;


	cout<<raw_tx->data<<endl;
	// cout<<sig_hash->data<<endl;
	free_Bins(reply);

	temp = new Bin(2);
  	memcpy(temp->data, "OK", temp->len);
  	requests.push_back(temp);
  	send(socket, requests);
	delete temp;

	return 1;

}