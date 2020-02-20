# -*-coding: utf-8-*-
from api.preprocess import preprocess, Status
from json import load, dump, loads
from collections import defaultdict


def find_matches():
    local_db = []

    data = []
    hand_match = []
    count = {}

    with open('items/globus.json', encoding='utf-8') as f:
        data.extend(load(f))

    with open('items/utkonos.json', encoding='utf-8') as f:
        data.extend(load(f))

    data = list(map(lambda x: x['data'], data))

    data = list(map(preprocess, data))

    for item in map(lambda x: x[0], filter(lambda x: x[1] == Status.OK, data)):
        if item['product_name'] not in count:
            count[item['product_name']] = [item]
        else:
            count[item['product_name']].append(item)

        for other in local_db:
            if item['match_2'] == other['match_2'] and item['match_3'] == other['match_3'] and ''.join(item['brand'].lower().split()) == ''.join(other['brand'].lower().split()) and item['egg_cat'] == other['egg_cat'] and item['yogurt'] == other['yogurt'] and item['milk'] == other['milk'] and item['butter'] == other['butter']:
                count[item['product_name']].append(other)

        local_db.append(item)

    with open('match_results.json', 'w', encoding='utf-8') as f:
        dump(count, f, ensure_ascii=False)


def print_success():

    def has_word(word, lst):
        for item in lst:
            if item['source'] == word:
                return True
        return False

    with open('match_results.json', 'r', encoding='utf-8') as f:
        res = load(f)

    data = dict(filter(
        lambda x: len(x[1]) > 1 and all((has_word('utkonos', x[1]), has_word('globus', x[1]))), res.items()))
    with open('successful_results.json', 'w', encoding='utf-8') as f:
        dump(data, f, ensure_ascii=False)
    print(f'Successful: {len(data)} of {len(res)}')


def test_for_brand():
    data = []
    counter = 0

    with open('items/globus.json', encoding='utf-8') as f:
        data.extend(load(f))

    with open('items/utkonos.json', encoding='utf-8') as f:
        data.extend(load(f))

    data = list(map(lambda x: x['data'], data))
    for i in data:
        if i['brand'].lower() in i['product_name'].lower():
            counter += 1

    print(f'{counter}/{len(data)}')


def hand_match():
    j1 = preprocess({
        "task_id": "4a09cb8e-55f8-4ab0-8015-c91958b00f0b",
        "segment": "milk",
        "operation": "",
        "federal_subject": "",
        "source": "perekrestok",
        "url": "https://www.perekrestok.ru/catalog/moloko-syr-yaytsa/slivki/domik-v-derevne-slivki-pit-ster-10-750g--310820",
        "brand": "Домик в деревне",
        "product_name": "Сливки Домик в деревне 10% 735мл",
        "product_type": "",
        "price_main": 170.9,
        "price_2": 170.9,
        "price_unit": "шт",
        "producer": "Вимм-Биль-Данн",
        "country": "Россия",
        "composition": "Сливки, молоко цельное",
        "standart": "ГОСТ 31451-2013",
        "pack_type": "Тетрапак",
        "packing": "",
        "expiration_period": "120 дней",
        "temperature_min": 2.0,
        "temperature_max": 25.0,
        "expiration_value": "120",
        "article_num": "310820",
        "department": "Сливки",
        "energy": 118.0,
        "protein": 2.7,
        "fats": 10.0,
        "carbohydrates": 4.4,
        "taste": "Без добавок",
        "weight": "",
        "weight_max": "",
        "weight_min": "",
        "weight_average": "",
        "fatness": 10.0,
        "descriptions": "Сливки Домик в деревне 10% 735мл приготовлены из свежего отборного молока, прошедшего строгий контроль качества. Они имеют нежный сливочный вкус и идеально подходят к чашечке кофе или чая, используются в кулинарии для приготовления десертов, муссов, а также как средство для загущения соусов, кремовых супов и горячих блюд. Продукт не содержит искусственных добавок и консервантов. Упакованы в пакет Tetra Pak с герметичной крышечкой. Открытую упаковку следует хранить в холодильнике и употребить в течение нескольких дней.",
        "processing_method": "Стерилизованные",
        "additives": "",
        "raw_type": "Коровье",
        "volume": "735 мл",
        "thermal_state": "",
        "marking": "",
        "eggs_category": "",
        "eggs_cnt": None,
        "color": "",
        "faetures": "",
        "salt": "",
        "min_age": "",
        "form": "",
        "sort": "",
        "product_kind": ""
    })[0]

    j2 = preprocess({
        "task_id": "51ae6615-2a27-4d6d-9980-f8cb80273e2b",
        "segment": "utkonos",
        "operation": "",
        "federal_subject": "",
        "source": "utkonos",
        "url": "https://www.utkonos.ru/item/3060250/slivki-domik-v-derevne-10--750-g",
        "product_name": "Сливки Домик в деревне 10% 750г",
        "price_main": 195.0,
        "brand": "Домик в деревне",
        "fatness": "10",
        "country": "Россия",
        "raw_type": "Коровье",
        "features": "",
        "pack_type": "",
        "weight": 0.75,
        "expiration_period": "от 46 до 120 суток",
        "article_num": 3060250.0,
        "energy": 118.0,
        "protein": None,
        "fats": 10.0,
        "carbohydrates": 4.4,
        "product_type": "Сливки питьевые",
        "description": "Описание и характеристики Сливки подходят не только для выпечки, десертов и сладостей. Они также великолепно сочетаются с морепродуктами, красной и белой рыбой, различными видами мяса и птицы. Вкус этих сливок яркий и обволакивающий, молочно-сладкий, а в аромате слышатся нотки парного деревенского молока. Благодаря невысокой жирности сливки не очень густые по консистенции. Их удобно использовать в готовке: блюдо дольше «томится», а его вкус становится более нежным, а аромат успевает полностью раскрыться. Состав: сливки, молоко цельное. Энергетическая ценность: 118 ккал. Пищевая ценность на 100г: жиры -10г, белки -2,7г, углеводы - 4,4г. Хранить при Т от 0'C до +25'C. Открытый пакет рекомендуется хранить в холодильнике при температуре от +2 до +6'C Срок годности 4 месяца. ГОСТ Р 52091 ОАО \"Вимм-Билль-Данн, Россия.",
        "big_cat": "Молоко, сыр, яйцо",
        "cat": "Молоко, сливки",
        "small_cat": "Сливки"
    })[0]

    print(j1['match_2'], j2['match_2'])
    print(j1['match_3'], j2['match_3'])
    print(j1['brand'], j2['brand'])
    print(j1['egg_cat'], j2['egg_cat'])
    print(j1['yogurt'], j2['yogurt'])
    print(j1['milk'], j2['milk'])
    print(j1['butter'], j2['butter'])


def get_brands():

    data = []

    with open('items/globus.json', encoding='utf-8') as f:
        data.extend(load(f))

    with open('items/utkonos.json', encoding='utf-8') as f:
        data.extend(load(f))

    data = list(map(lambda x: x['data']['brand'], data))
    print(len(sorted(set(data))))


def weight_test():
    from math import ceil
    w = 950
    coef = 50 if w >= 200 else 10
    w = ceil(w / coef) * coef
    print(w)


# find_matches()
# print_success()
# test_for_brand()
# hand_match()
weight_test()
