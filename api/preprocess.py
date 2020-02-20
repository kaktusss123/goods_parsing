# -*-coding:utf-8-*-
from json import load
from enum import Enum
from re import search, IGNORECASE, findall, match, sub
from math import ceil

with open('api/available_types.json', encoding='utf-8') as f:
    types = set(load(f))

with open('api/replacements.json', encoding='utf-8') as f:
    replacements = load(f)

with open('api/brand_repl.json', encoding='utf-8') as f:
    brand_repl = load(f)


class Status(Enum):
    OK = 0
    BAD_CATEGORIES = 1
    BAD_RESPONSE = 2
    FINISHED = -1


def set_match_params(json: dict) -> dict:
    """Set fields for item matching

    :param json: data
    :type json: dict
    :return: data with new fields
    :rtype: dict
    """
    json['brand'] = json['brand'].replace('й', 'й').replace('ё', 'е')
    json['product_name'] = json['product_name'].replace(
        'й', 'й').replace('ё', 'е')

    # FIXME тут что-то бесполезное
    tmp = search(f'{json["brand"]}.+?(?=\\s\\d)',
                 json['product_name'], IGNORECASE)
    json['match_1'] = tmp.group(0) if tmp is not None else ''

    tmp = search(r'[\d.,-]+%', json['product_name'], IGNORECASE)
    json['match_2'] = '' if tmp is None else tmp.group(
        0).lower().replace(' ', '').replace('.', ',')

    tmp = search(r'\d[\d.,*-]*\s?(?=(л|мл|г|кг|шт))(?!\*)',
                 json['product_name'], IGNORECASE)
    json['match_3'] = 0 if tmp is None else tmp.group(
        0).lower().replace(' ', '').replace(',', '.')
    try:
        json['match_3'] = float(json['match_3'])
        # 0,95 == 950
        if json['match_3'] <= 1:
            json['match_3'] *= 1000
        # округление
        coef = 50 if json['match_3'] >= 200 else 10
        json['match_3'] = ceil(json['match_3'] / coef) * coef
    except:
        pass

    tmp = search(r'(?<!\w)[CС]\d|[BВ](?!\w)', json['product_name'])
    json['egg_cat'] = tmp.group(0) if tmp is not None and json['product_name'].replace('CO', 'C0').replace('СО', 'С0').lower(
    ).strip().startswith('яйц') else ''

    json['yogurt'] = '|'.join(sorted(set(findall(r'клубни(?=[кч])|черносл|отруб|вишн|черни(?=[кч])|цитрус|персик|кокос|груш|личи|киноа|овес|куркум|манго|ежеви(?=[кч])|малин|тыкв|банан|абрикос|облепих|виноград|чиа|матча|ананас|шоколад|крем-брюле|злак|сливк|имбир|лимон|ваниль|мед|орех|морков|мюсл|пломбир|крыжовн|ягод|гранол|печенье|земляни(?=[кч])|папайя|клюкв|маракуй|черешн|карамель|кумкват|дын|апельсин|голуби(?=[кч])|лаванд|яблок|традиц|кориц|инулин|натурал|капучино|лайм|мят|сорбет|арбуз|зефир|роз(?=[аы])|ната де коко',
                                                 json['product_name'], IGNORECASE)))).lower() if 'йогурт' in json['product_name'].lower() else ''
    json['milk'] = '|'.join(sorted(set(findall(
        r'топленое|ультрапастеризован|кобыл|коз|пастеризован|отборн|кокос|сгущенное|сахар|стерилизован|низколактоз|безлактоз|zero|low|концентрирован|овсян|соев', sub(r'безлактоз\w+', sub(r'низколактоз\w+', 'Low Lactose', json['product_name'], flags=IGNORECASE), 'Zero Lactose', flags=IGNORECASE), flags=IGNORECASE)))).lower() if 'молоко' in json['product_name'].lower() else ''

    json['butter'] = '|'.join(sorted(set(findall(
        r'сливочн|традиц|крестьянск|топлен|шоколад|фасов|упаков|(не)?солен', json['product_name'], IGNORECASE)))).lower() if 'масло' in json['product_name'].lower() else ''

    return json


def filter_cat(json: dict) -> Status:
    """Filter only available categories

    :param json: data from kafka
    :type json: dict
    :return: status
    :rtype: Status
    """
    # FIXME: придумать фильтрацию типов
    return Status.OK
    # if json.get('big_cat') in types and json.get('cat') in types and json.get('small_cat') in types:
    #     return Status.OK
    # return Status.BAD_CATEGORIES


def replace(string: str, repl: dict) -> str:
    """Replace old categories of product

    :param string: old category
    :type string: str
    :param repl: dict with replacements
    :type repl: dict
    :return: new category
    :rtype: str
    """
    for k, v in repl.items():
        string = string.replace(v, k)
    return string


def replace_brands(string: str, repl: dict) -> str:
    """Replace brands by regexs

    :param string: old brand
    :type string: str
    :param repl: dictionary for replacement
    :type repl: dict
    :return: new brand
    :rtype: str
    """
    for k, v in brand_repl.items():
        if match(k, string, IGNORECASE):
            return v
    return string


def preprocess(json: dict) -> tuple:
    """Function for preprocess parsed data obtained from kafka

    :param json: parsed data
    :type json: dict
    :return: dict, status
    :rtype: tuple
    """

    # Filter empty records
    if not json.get('product_name'):
        return json, Status.BAD_RESPONSE

    # Filter categories
    status = filter_cat(json)

    if 'яйц' in json['product_name'].lower():
        json['big_cat'] = 'Яйца'

    json['brand'] = replace_brands(json['brand'], brand_repl)

    # Replace categories
    # FIXME: победить категории
    # json['big_cat'] = replace(json['big_cat'], replacements)
    # json['cat'] = replace(json['cat'], replacements)
    # json['small_cat'] = replace(json['small_cat'], replacements)

    # Gaining mass, product_name
    json = set_match_params(json)
    return json, status
