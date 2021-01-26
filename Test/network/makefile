objects = validate_proof.o network.o utility.o
validata_proof : $(objects)
	g++ -w -o validate_proof $(objects) -lzmq -lssl -lcrypto -lpthread -L/usr/local/lib
#计算hash需要-lssl -lcrypto 

validate_proof.o : 
	g++ -w -c validate_proof.cpp 
network.o:
	g++ -w -c network.cpp
utility.o:
	g++ -w  -c utility.cpp

.PHONY : clean
clean :
	rm validate_proof $(objects)