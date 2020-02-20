from lxml.html import fromstring as fs
from aiohttp import ClientSession, ClientTimeout
from queue import Queue
import asyncio
from random import choice
from json import dump

DONE = -1
CRAWL_LIMIT = 5
RETRY_COUNT = 50

base = 'https://www.utkonos.ru'
start_url = 'https://www.utkonos.ru/cat/4405'
pagination_path = "//span[@class='selected']/following-sibling::a[1]/@href"
item_path = "//div[@class='goods_view_box-caption']/a[@class='goods_caption']/@href"
harks = {
    'table': r"//div[@class='goods_view_item-property_title']/text()"
}


def get_proxy():
    '''Получить свежие прокси Натана'''
    import requests
    proxy_url = 'http://10.199.13.39:8085/get_data'
    proxy_lim = 100
    proxy_offset = 86500
    json = {}
    json['topic'] = 'proxies'
    json['time_offset'] = proxy_offset
    json['amount'] = proxy_lim
    json['filter'] = ['schema', ['https']]
    resp = requests.post(proxy_url, json=json).json()
    resp = list(map(lambda x: x.get('value', {}).get(
        'proxy', '').replace('https', 'http'), resp))
    return resp


proxies = get_proxy()


async def crawl(sess, q):
    nxt = start_url
    url_counter = 0
    while url_counter < CRAWL_LIMIT:
        for try_count in range(RETRY_COUNT):
            try:
                p = choice(proxies)
                print(
                    f'Trying get pagination {nxt}, attempt {try_count}, proxy: {p}')
                page = await sess.get(nxt, proxy=p)
                if page.status == 200:
                    page = fs(await page.text())
                    url_counter += 1
                    break
            except Exception as e:
                print(f'{e.__class__.__name__}: {e}')
        else:
            print('Connection error!')
            await q.put(DONE)
            return
        items = page.xpath(item_path)
        for i in items:
            await q.put(i)
        try:
            nxt = page.xpath(pagination_path)[0]
            print(f'Crawled {nxt}')
        except IndexError:
            print('No next pagionation!')
            await q.put(DONE)
            return


async def scrap(sess, q):
    res = []
    elem = await q.get()
    while elem != DONE:
        for try_count in range(RETRY_COUNT):
            p = choice(proxies)
            print(f'Trying get item {elem}, attempt {try_count}, proxy: {p}')
            try:
                page = await sess.get(base + elem, proxy=p)
                if page.status == 200:
                    page = fs(await page.text())
                    break
            except Exception as e:
                print(f'{e.__class__.__name__}: {e}')
        else:
            print('No item!')
            continue
        for k, v in harks.items():
            res = set(page.xpath(v))
        res = {x.strip() for x in res}
        print(f'Item {elem} scraped!')
        with open('items.json', 'a', encoding='utf-8') as f:
            dump(list(res), f, ensure_ascii=False)
            f.write('\n')


async def main():
    queue = asyncio.Queue()
    async with ClientSession(timeout=ClientTimeout(total=10)) as sess:
        futures = [asyncio.ensure_future(crawl(sess, queue))]
        futures += [asyncio.ensure_future(scrap(sess, queue))
                    for _ in range(50)]
        await asyncio.wait(futures)

asyncio.run(main())
