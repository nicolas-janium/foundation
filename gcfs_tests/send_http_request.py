import requests

payload = {
    "from": "retool",
    "client_id": "e98f3c45-2f62-11eb-865a-42010a3d0004" 
}

res = requests.post(url='localhost:8080', data=payload)
if res.ok:
    print(res.text)