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

void HexStrToByte(unsigned const char* source, unsigned char* dest, int sourceLen)
{
  short i;
  unsigned char highByte, lowByte;

  for (i = 0; i < sourceLen; i += 2)
  {
    highByte = toupper(source[i]);
    lowByte = toupper(source[i + 1]);

    if (highByte > 0x39)
    highByte -= 0x37;
    else
    highByte -= 0x30;

    if (lowByte > 0x39)
    lowByte -= 0x37;
    else
    lowByte -= 0x30;

    dest[i / 2] = (highByte << 4) | lowByte;
  }
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

void printBytes(unsigned char *md, int len) 
//注意打印16进制数组要用这种方式，不能用cout<<md<<endl;因为md中没有字符串结束符'\0'
{

  for(int i = 0; i < len; i++) 
  {
    std::cout<<md[i];
  }
  std::cout<<std::endl;
  return ;
}

void printHex(unsigned char *md, int len)
{
    int i = 0;
    for (i = 0; i < len; i++)
    {
        printf("%02x", md[i]);
    }
 
    printf("\n");
}

std::string charArray_to_String(unsigned char* buf,int len)
//不能用string str = (const char*)buf直接转化，因为这里SHA函数输出buf字符串没有结束符。
{
  std::string str;
  str.assign((const char*)buf,len); 
  return str;
}

