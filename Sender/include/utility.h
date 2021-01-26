#ifndef UTILITY__h
#define UTILITY__h

#include <string>
#include <vector>
#include <iostream>
#include <cstring>
#include "CJsonObject.hpp"

struct Bin
{
    unsigned char * data;
    int len;
    int flag;
    Bin(){};
  	Bin(int len_c);
  	void print();
};
void print_hex(int len, unsigned char *data);

bool defined(Bin* item);

void delete_bin(Bin* item);

void HexStrToByte(unsigned const char* source, unsigned char* dest, int sourceLen);

void* tmalloc(size_t size);

void printBytes(unsigned char *md, int len) ;

void printHex(unsigned char *md, int len);

std::string charArray_to_String(unsigned char* buf,int len);


#endif