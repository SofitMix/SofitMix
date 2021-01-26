#ifndef UTILITY__h
#define UTILITY__h

#include <string>
#include <vector>
#include <iostream>
#include <cstring>
#include <string.h>


struct Bin
{
    unsigned char * data;
    int len;

    Bin(){};
  	Bin(int len_c);
  	void print();
};
void print_hex(int len, unsigned char *data);
bool defined(Bin* item);
void delete_bin(Bin* item);
void* tmalloc(size_t size);
std::string* byteToHexStr(unsigned char byte_arr[], int arr_len);

#endif