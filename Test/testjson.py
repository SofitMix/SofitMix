#! usr/bin/python3
import json


# mes = ["a11","a22",]
# with open("test.json","w") as file:
# 	json.dump(mes,file)
# with open("test.json","r") as file:
# 	megs = json.load(file)
# 	print(megs)
with open("test.json","r") as file:
	content = file.read()
	print(content[13])
