objects = ZK.o network.o CJsonObject.o utility.o cJSON.o
ZK : $(objects)
	g++ -o ZK $(objects) -lzmq -ljsoncpp -lssl -lcrypto -pthread -L/usr/local/lib
#计算hash需要-lssl -lcrypto 

ZK.o : 
	g++ -c ZK.cpp 
network.o:
	g++ -c network.cpp
utility.o:
	g++ -c utility.cpp
CJsonObject.o:
	g++ -w -c CJsonObject.cpp
cJSON.o:
	gcc -w -c cJSON.c

.PHONY : clean
clean :
	rm ZK $(objects)