import pandas as pd
from json import load
from itertools import zip_longest as zip

# for item in ['globus_electrostal.json', 'globus_ryazan.json', 'globus_tver.json']:
#     with open(f'items/{item}', 'r', encoding='utf-8') as f:
#         data = load(f)

#     data = list(map(lambda x: x['data'], data))

#     pd.DataFrame.from_dict(data).to_excel(f'{item.split(".")[0]}.xlsx')
#     print(item)


# print(df.big_cat.unique())
# print(df.cat.unique())
# print(df.small_cat.unique())


lst = []

for item in ['globus.json', 'utkonos.json']:
    with open(f'items/{item}', 'r', encoding='utf-8') as f:
        data = load(f)

    data = list(map(lambda x: x['data'], data))
    df = pd.DataFrame.from_dict(data)
    lst += list(df.big_cat.unique())
    lst += list(df.cat.unique())
    lst += list(df.small_cat.unique())

print(sorted(lst), len(lst))
big_cat = ['Молоко, сыр, яйцо', 'Крупы, масло, консервы, соусы, орехи',
           'Детское питание, уход, игрушки', 'Замороженные продукты, мороженое', 'Вода, соки, напитки']
cat = ['Сливочное масло, маргарин', 'Соусы, майонез',
       'Кефир, ряженка, кисломолочные продукты', 'Детское питание',
       'Молоко, сливки', 'Сметана', 'Сыры', 'Яйцо',
       'Йогурты, творожки, молочные коктейли, сгущенка',
       'Национальные молочные продукты', 'Творог, сырки, творожная масса',
       'Растительные молочные продукты', 'Консервы, варенье, мед',
       'Майонез, заправки для салата', 'Мороженое', 'Детские молочные продукты',
       'Торты, пирожные, пироги, кексы', 'BioMax',
       'Энергетические, кофейные напитки']
small_cat = ['Майонез', 'Кефир', 'Молочное детское питание',
             'Молоко', 'Мягкие, рассольные, копченые', 'Полутвёрдые, твёрдые', 'Творожные, плавленые', 'Сливки',
             'Йогурты', 'Десерты', 'Творог', 'Сырки, запеканки, десерты', 'С плесенью', 'Напитки для иммунитета',
             'Сгущенка', 'Творожки', 'Кисломолочные напитки', 'Молочные коктейли', 'Премиальные', 'Закваска',
             'Соевые', 'Постное', 'Сырные тарелки, наборы для фондю', 'Пирожные', 'Здоровое меню', 'Пюре', 'Вода, соки, напитки']

# pd.DataFrame(zip(big_cat, cat, small_cat), index=None).to_excel('types.xlsx')
