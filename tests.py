import requests
from uuid import uuid4
import json
from pprint import pprint
import timeit
from random import randint

offers = [
    {
      "id": str(uuid4()),
      "name": f"Товар {randint(100, 999)}",
      "parentId": None,
      "type": "OFFER",
      "price": randint(100, 999)
    }
    for i in range(1000)]


data = {
  "items": offers,
  "updateDate": "2022-05-28T21:12:01.000Z"
}

s = timeit.default_timer()
resp = requests.post('http://localhost:80/imports', data=json.dumps(data))
print(resp.status_code)
print('Time: ', timeit.default_timer() - s)

s = timeit.default_timer()
resp = requests.get('http://localhost:80/sales?date=2022-05-28T21:12:01.000Z')
print(resp.status_code)
#pprint(resp.json())
print('Time: ', timeit.default_timer() - s)

