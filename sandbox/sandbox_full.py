import json
import uuid
from aiohttp import ClientSession
import asyncio
from aiokafka import AIOKafkaConsumer
from requests import post
import pprint
from termcolor import cprint
import re
from sys import argv

SPIDERS_DICT = {
    6805: '78.157.221.27',
    6806: '78.157.221.43',
    6807: '78.157.221.45',
}


async def listen_kafka(task_id, items):
    consumer = AIOKafkaConsumer(
        'data', 'finished',
        loop=asyncio.get_event_loop(),
        # bootstrap_servers='78.157.221.27:9091, 78.157.221.43:9091, 78.157.221.45:9091',
        bootstrap_servers='10.199.13.36:9091, 10.199.13.37:9092, 10.199.13.38:9093',
        value_deserializer=lambda m: json.loads(m.decode('utf8')))
    await consumer.start()
    async for msg in consumer:
        if msg.topic == 'data':
            if msg.value.get('task_id') == task_id:
                item = msg.value
                print(len(items) + 1, item)
# ------------------------------------------------------------------------------------------------------>
                # print(str(len(items) + 1)+')', item['data']['segment_subtype'],'#',item['data']['url'])
# ----------------------------------------------------- ------------------------------------------------->
                items.append(item)
        elif msg.topic == 'finished':
            if msg.value.get('task_id') == task_id:
                break
    await consumer.stop()


async def process_task(items, filename):
    # with open(r'C:\Users\user1\Documents\instruction\multilisting_gar\multilisting_gar.json', encoding='utf-8') as fp:
    with open(filename, encoding='utf-8') as fp:
        data = json.load(fp)

    task_id = str(uuid.uuid4())
    items_lst = asyncio.ensure_future(listen_kafka(task_id, items))
    data['_task_id'] = task_id
    data['project_id'] = 'metaspider'
    data['spider_id'] = 'metacrawler'
    data['global_settings']['CONCURRENT_REQUESTS'] = 256
    data['global_settings']['CLOSESPIDER_ERRORCOUNT'] = 1000
    data['global_settings']['CONCURRENT_REQUESTS_PER_DOMAIN'] = 256
    data['global_settings']['AUTOTHROTTLE_TARGET_CONCURRENCY'] = 256
    data['global_settings']['LOG_LEVEL'] = 'DEBUG'
    data['global_settings']['CLOSESPIDER_ITEMCOUNT'] = 10000000
    data['global_settings']['SCHEDULER_DISK_QUEUE'] = 'scrapy.squeues.PickleLifoDiskQueue'

    # pprint.pprint(data)

    async with ClientSession() as session:
        spider = await get_least_busiest_server_port(session)
        print('send task to {}'.format(spider))
        async with session.post('http://{}/crawl.json'.format(spider), json=data) as response:
            print('task {} sent'.format(task_id))
# ------------------------------------------------------------------------------------------------------------>
            with open(r'task_name.json', 'w', encoding='utf-8') as fp:
                json.dump({"task_id": task_id}, fp,
                          ensure_ascii=False, indent=4)
                cprint('Номер задачи сохранен в task_name.json', 'green')
# ------------------------------------------------------------------------------------------------------------>
            print((await response.read()).decode().strip())

    await items_lst
    with open(f'items1.json' if len(argv) <= 2 else f'items/{argv[2]}', 'w', encoding='utf-8') as fp:
        json.dump(items, fp, ensure_ascii=False)

    print('{} items saved'.format(len(items)))


async def fetch_status(url, session):
    async with session.get('http://{}/daemonstatus.json'.format(url)) as response:
        data = json.loads((await response.read()).decode().strip())
        data['url'] = url
        return data


async def get_least_busiest_server_port(session):
    tasks = []
    for port, host in SPIDERS_DICT.items():
        task = asyncio.ensure_future(fetch_status(
            '{}:{}'.format(host, port), session))
        tasks.append(task)
    responses = await asyncio.gather(*tasks)
    servers_list = sorted(
        [(r['pending'] + r['running'], r['url']) for r in responses])
    return servers_list[0][1]


loop = asyncio.get_event_loop()
items = []
filename = argv[1]
try:
    loop.run_until_complete(process_task(items, filename))
finally:
    new_items = []
    for data in items:
        new_dict = {}
        new_dict['offset'] = 0
        new_dict['partition'] = 0
        new_dict['value'] = data
        new_items.append(new_dict)

    # with open(r'C:\Users\user1\Documents\instruction\irr_zag\items.json', 'w', encoding='utf-8') as fp:
    with open(r'items_2.json', 'w', encoding='utf-8') as fp:
        json.dump(new_items, fp, ensure_ascii=False, indent=4)
