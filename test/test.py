import requests

BASE = "http://127.0.0.1:5000/"

data = [{"name":"Test1", "price": 12},
        {"name":"Test2", "price": 14},
        {"name":"Test3", "price": 4},
        {"name":"Test4", "price": 11},
        {"name":"Test5", "price": 42},
        {"name":"Test6", "price": 61}]

for i in range(len(data)):
    response = requests.put(BASE + "item/" + str(i), data[i])
    print (response.json())
    
input()

response = requests.get(BASE + "item/all")
print (response.json())