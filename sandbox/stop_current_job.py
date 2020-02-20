from requests import post
from time import sleep
from json import loads, load
from pprint import pprint as print

with open('task_name.json', encoding='utf-8') as f:
    task_id = load(f)['task_id']
    print(task_id)

r = loads(post('http://10.199.13.39:8181/cancel',
               json={"_task_id": task_id, "force": True}, headers={'Content-Type': 'application/json'}).text)
print(r)
