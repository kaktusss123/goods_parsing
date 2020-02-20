from json import loads

s = set()
with open('items.json', encoding='utf-8') as f:
    for line in f:
        for item in loads(line):
            s.add(item)

print(s)
