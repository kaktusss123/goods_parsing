import pandas as pd
from functools import reduce
from preprocess import preprocess, Status
from json import load


def match(args):

    operations = [
        lambda x, y: x['match_2'] == y['match_2'],
        lambda x, y: x['match_3'] == y['match_3'],
        lambda x, y: ''.join(x['brand'].lower().split()) ==
        ''.join(y['brand'].lower().split()),
        lambda x, y: x['egg_cat'] == y['egg_cat'],
        lambda x, y: x['yogurt'] == y['yogurt'],
        lambda x, y: x['milk'] == y['milk'],
        lambda x, y: x['butter'] == y['butter']
    ]

    cols = [(f'{args[1][0]}_{i}', f'price_{i}') for i in range(10)]
    cols = [f'{args[0][0]}', f'{args[0][0]}_price'] + \
        [item for sublist in cols for item in sublist]
    res = pd.DataFrame(columns=cols)

    items = {}

    for arg in args:
        with open(f'items/{arg[1]}', encoding='utf-8') as f:
            items[arg[0]] = list(
                map(preprocess, map(lambda x: x.get('data') or x['value']['data'], load(f))))
            items[arg[0]] = list(map(lambda x: x[0], filter(
                lambda x: x[1] == Status.OK, items[arg[0]])))
            if 'price_sub' in items[arg[0]][0]:
                for rec in items[arg[0]]:
                    rec['price_main'] += rec['price_sub'] / 100

    banned_g, banned_u = set(), set()

    for g in items[args[0][0]]:
        matched = []
        if not g['brand']:
            continue
        for u in items[args[1][0]]:
            if not u['brand']:
                continue
            if all([func(g, u) for func in operations]):
                banned_u.add(u['product_name'])
                matched.extend([u['product_name'], u['price_main']])
        if matched:
            banned_g.add(g['product_name'])
            matched = [g['product_name'], g['price_main']] + matched
            res = res.append(dict(zip(cols, matched)), ignore_index=True)

    unbanned_g = pd.DataFrame(columns=['Наименование', 'Цена'])
    unbanned_u = pd.DataFrame(columns=['Наименование', 'Цена'])
    for g in items[args[0][0]]:
        if g['product_name'] not in banned_g:
            unbanned_g = unbanned_g.append(
                {'Наименование': g['product_name'], 'Цена': g['price_main']}, ignore_index=True)

    for g in items[args[1][0]]:
        if g['product_name'] not in banned_u:
            unbanned_u = unbanned_u.append(
                {'Наименование': g['product_name'], 'Цена': g['price_main']}, ignore_index=True)

    ### Statistics ###
    stat = pd.DataFrame(
        columns=['source', 'full', 'matched', 'match_pct'])
    stat = stat.append({'source': args[0][0], 'full': len(items[args[0][0]]), 'matched': len(
        res), 'match_pct': f'{len(res) / len(items[args[0][0]]) * 100:.2f}%'}, ignore_index=True)
    stat = stat.append({'source': args[1][0], 'full': len(items[args[1][0]]), 'matched': len(
        res), 'match_pct': f'{len(res) / len(items[args[1][0]]) * 100:.2f}%'}, ignore_index=True)

    return res, unbanned_g, unbanned_u, stat


ut, gl, pe = ('utkonos', 'utkonos.json'), ('globus',
                                           'globus.json'), ('perekrestok', 'PEREKR_item_2.json')

# ut, gl, pe = ('globus', 'globus.json'), ('globus_tver',
#                                          'globus_tver.json'), ('globus_ryazan', 'globus_ryazan.json')

for e in ((ut, pe), (gl, pe), (gl, ut)):
    m, g, u, stat = match(e)
    with pd.ExcelWriter(f'result_{e[0][0]}_{e[1][0]}.xlsx') as writer:
        m.to_excel(writer, index=False, sheet_name='Совпадение')
        g.to_excel(writer, index=False, sheet_name=e[0][0])
        u.to_excel(writer, index=False, sheet_name=e[1][0])
        stat.to_excel(writer, index=False, sheet_name='Статистика')
