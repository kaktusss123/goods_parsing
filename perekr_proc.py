from json import load, dump

with open('items/PEREKR_item_2.json', encoding='utf-8') as f:
    data = load(f)

for item in data:
    item['value']['data']['product_kind'] = item['value']['data']['product_type']
    item['value']['data']['product_type'] = item['value']['data']['product_name']
    item['value']['data']['product_name'] = item['value']['data']['title']
    del item['value']['data']['title']

with open('items/PEREKR_item_2.json', 'w', encoding='utf-8') as f:
    dump(data, f, ensure_ascii=False, indent=2)
