#include "utility.h"

Bin::Bin(int len_c){
  len = len_c;
  data = (unsigned char *) tmalloc(len);
}

void Bin::print(){

  if (len == 0){
    printf("Bin was freed, or is invalid!\n");
    return;
  }

  printf("Len is: %d\n", len);
  printf("Hex is: \n");
  print_hex(len, data);
  printf("\n");
}


bool defined(Bin* item){
  return !(item == NULL || item->len < 1);
}

void delete_bin(Bin* item){
  if (item != NULL){
    delete item;
    item = NULL;
  }
}

void print_hex(int len, unsigned char *data){
  int x;
  for(x=0;x<len;x++){
    printf("%02x", data[x]);
  }
  printf("\n");
}

void* tmalloc(size_t size)
{
  void* res = malloc(size);
  if (res == NULL) {
    exit(-3);
  }
  memset(res, 0 , size);
  return res;
}

std::string* byteToHexStr(unsigned char byte_arr[], int arr_len)
{  
  std::string* hexstr=new std::string(); 
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

