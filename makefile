CC = g++
CFLAGS = -w
LDFLAGS = -lzmq -ljsoncpp -lssl -lcrypto -lpthread -L/usr/local/lib



all: validate_proof ZK

###########################################################################
## validate_proof
###########################################################################
validate_proof_BIN = Mixer/bin/
validate_proof_PATH = Mixer/
validate_proof_INCLUDE = -I Mixer/include

validate_proof_SOURCES = /validate_proof.cpp /network.cpp /utility.cpp 
validate_proof_OBJECTS = $(subst /,$(validate_proof_BIN),$(validate_proof_SOURCES:.cpp=.o)) #Mixer/bin/validate_proof.o...
validate_proof_TARGET = validate_proof
DEPEND = $(validate_proof_OBJECTS)

# Compile Objects
$(validate_proof_OBJECTS):
	$(CC) $(CFLAGS) -c $(subst $(validate_proof_BIN),$(validate_proof_PATH), $(@:.o=.cpp)) -o $@ $(validate_proof_INCLUDE)
#$@--目标文件，$^--所有的依赖文件，$<--第一个依赖文件
#$(subst $(BIN),$(UTILITY), $(@:.o=.cpp)): src/utility/utility.cpp...

# Compile Targets
$(validate_proof_TARGET) : $(DEPEND)
	$(CC) $(CFLAGS) -o $(validate_proof_BIN)$@ $^ $(validate_proof_INCLUDE) $(LDFLAGS)


###########################################################################
## ZK
###########################################################################
ZK_BIN = Sender/bin/
ZK_PATH = Sender/
ZK_INCLUDE = -I Sender/include

ZK_SOURCES = /ZK.cpp /network.cpp /utility.cpp /CJsonObject.cpp 
ZK_OBJECTS = $(subst /,$(ZK_BIN),$(ZK_SOURCES:.cpp=.o)) #Sender/bin/ZK.o...
ZK_TARGET = ZK
DEPEND = $(ZK_OBJECTS) $(ZK_BIN)cJSON.o

# Compile Objects
$(ZK_OBJECTS):
	$(CC) $(CFLAGS) -c $(subst $(ZK_BIN),$(ZK_PATH), $(@:.o=.cpp)) -o $@ $(ZK_INCLUDE)
$(ZK_BIN)cJSON.o:
	gcc -w -c $(ZK_PATH)cJSON.c -o $@ $(ZK_INCLUDE)
#$@--目标文件，$^--所有的依赖文件，$<--第一个依赖文件
#$(subst $(BIN),$(UTILITY), $(@:.o=.cpp)): src/utility/utility.cpp...

# Compile Targets
$(ZK_TARGET) : $(DEPEND)
	$(CC) $(CFLAGS) -o $(ZK_BIN)$@ $^ $(ZK_INCLUDE) $(LDFLAGS)


clean:
	rm -rf $(validate_proof_BIN)* $(ZK_BIN)*

