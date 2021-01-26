import requests
from bs4 import BeautifulSoup
import re
import json
import time
import bitcoin.rpc
from bitcoin.core import *
from bitcoin.core.script import *

PORT = 18333
bitcoin.SelectParams('testnet')
proxy = bitcoin.rpc.Proxy()
# url = "https://www.blockchain.com/btctest/address/2N3WgvrBdKfFApyETyAiQEEuWDGrYL2PQfU"
def check_address(address):
    url = "https://www.blockchain.com/btctest/address/"+address
    params = {

    }
    headers = {
        "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        
        "accept-language":"zh-CN,zh;q=0.9,en;q=0.8",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    }
    verify = True
    proxies = {
    'https':'https://64.227.14.219:8080',
    'https':'https://34.90.113.143:3128',
    'https':'https://38.91.107.117:3128',
    'http':'http://142.93.57.37:80',
    'https':'https://159.203.207.56:3128'
    }
    # auth = ("username","password")
    timeout = 20
    r = requests.get(url,headers=headers,proxies = proxies, verify=verify,timeout=timeout)
    # r.encoding = 'utf-8'
    Data = r.text
    soup = BeautifulSoup(Data,'html.parser')
    br = re.compile(r'<.*?>')
    result = soup.find(attrs = {"id":"__NEXT_DATA__"}).get_text()
    json_result = json.loads(result)['props']["initialProps"]["pageProps"]["addressTransactions"]
    print(json.dumps(json_result,indent=4))
    return json_result

def check_address1(address):
    url = "https://www.blockchain.com/btctest/address/"+address
    params = {

    }
    headers = {
        "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",

        "accept-language":"zh-CN,zh;q=0.9,en;q=0.8",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    }
    verify = True
    proxies = {
    'https':'https://144.91.71.141:8080',
    'https':'https://157.245.151.11:3128',
    'https':'https://34.90.113.143:3128',
    'https':'https://165.227.220.35:3128',
    'http':'http://38.91.107.117:3128',
    'https':'https://159.203.207.56:3128'
    }
    # auth = ("username","password")
    timeout = 40
    r = requests.get(url,headers=headers, verify=verify,timeout=timeout)
    # r.encoding = 'utf-8'
    Data = r.text
    soup = BeautifulSoup(Data,'html.parser')
    br = re.compile(r'<.*?>')
    result = soup.find(attrs = {"id":"__NEXT_DATA__"}).get_text()
    json_result = json.loads(result)['props']["initialProps"]["pageProps"]["addressTransactions"]
    print(json.dumps(json_result,indent=4))
    return json_result
    

def main():    
    while True:
        time.sleep(10)
        try:
            with open("tx_info.json","r") as file:
                # [txid,server_pubkey,redeem_script]
                # 要拿到txid和redeem_script中的a
                block_info = json.load(file)
                keys = list(block_info.keys())
                blockcount = proxy.getblockcount()
                str_blockcount = str(blockcount)
                keys.append(str_blockcount)
                keys.sort()
                try:
                    for i in range(keys.index(str_blockcount)+1,len(keys)):
                        key = keys[i]
                        tx_info = block_info[key]
                        for info in tx_info:
                            redeemScript = CScript(info[2])
                            script_pub_key = redeemScript.to_p2sh_scriptPubKey()
                            p2sh_address = CBitcoinAddress.from_scriptPubKey(script_pub_key)
                            result = check_address(p2sh_address)
                            if len(result)>1:
                                for i in range(len(result)):
                                    if 'mempool' in result[i]['block'].key():
                                        txid = result[i]['inputs']['txid']
                                        sigscript = result[i]['inputs']['sigscript']
                                        script = sigscript[2+(int(script[0])*16+int(script[1]))*2:]
                                        a = x(script[2:(int(script[0])*16+int(script[1])+1)*2]) 
                                        print(txid)
                except ValueError as err:
                    pass
        except (json.JSONDecodeError, FileNotFoundError) as err:
            pass

address1="2N9h7pY7AykjcAKQcj4DWqhoZxsEYN5hsmn"
# address = "2MsRtc2eGFDAnzcUV4ZNfZFCqL4Sg7Ej3ez"
# address = "2NEfXeWu6KkRs2Y1BeTFtZsu14uK5cK9ZaT"
check_address1(address1)
# main()
# script = "473044022048e58abbf4e61d4b898544fe9c561fc5221c5b2f3b27df332ba62685d04d23d5022062e31c6f1a164cf64e70374f6375bd7201ae5185748930704b47d935961eda9701097a65726f6d69786572514c7263a820b1c303da4553b492e9950260369d20f1a016f5ffcb0de7dc1aa4779115b11004882102423738ab17d6328269c5fcd2772ba0a93223fc3da65dce38c68d76e6bf250d22ac6703ee6e19b1752102423738ab17d6328269c5fcd2772ba0a93223fc3da65dce38c68d76e6bf250d22ac68"
# sig_len = script[0:2]
# script = script[2+(int(script[0])*16+int(script[1]))*2:]
# a = script[2:(int(script[0])*16+int(script[1])+1)*2]
# print(x(a))
# a = 'zeromixer'
# print(a.encode())