import requests
import json
base='http://127.0.0.1:8000/api'
print('Registering user...')
resp = requests.post(f'{base}/user/register/', json={'username':'testbuyer2','password':'Buyer1234!','email':'tb2@example.com','tipo':'comprador','direccion':'Calle Test 2'})
print(resp.status_code, resp.text)
print('Requesting token...')
resp2 = requests.post(f'{base}/token/', json={'username':'testbuyer2','password':'Buyer1234!'})
print(resp2.status_code, resp2.text)
if resp2.status_code==200:
    access = resp2.json().get('access')
    h={'Authorization':f'Bearer {access}','Content-Type':'application/json'}
    payload={'items':[{'id':1,'cantidad':1,'precio':10.0}],'total':10.0,'estado':'pendiente','shipping':{'direccion':'Calle Test','ciudad':'Ciudad','telefono':'123'}}
    r = requests.post(f'{base}/pedidos/', json=payload, headers=h)
    print('POST pedidos:', r.status_code, r.text)
else:
    print('No token, skipping pedidos')
