objects = tumbler_server.o
# memory.o utility.o
tumbler_server : $(objects)
	g++ -o tumbler_server $(objects) -lzmq -lpthread -L/usr/local/lib

tumbler_server.o : 
	g++ -c tumbler_server.cpp 


.PHONY : clean
clean :
	rm tumbler_server $(objects)
