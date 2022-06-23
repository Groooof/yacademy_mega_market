import requests
from uuid import uuid4
import json
from pprint import pprint
import timeit
from random import randint
from enum import Enum
import json

# import ctypes
# kernel32 = ctypes.WinDLL('kernel32')
# hStdOut = kernel32.GetStdHandle(-11)
# mode = ctypes.c_ulong()
# kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode))
# mode.value |= 4
# kernel32.SetConsoleMode(hStdOut, mode)

PROTOCOL = 'http'
HOST = 'localhost'
PORT = 80


class Methods(Enum):
    get = 'GET'
    post = 'POST'
    delete = 'DELETE'


map_methods = {
    Methods.get: requests.get,
    Methods.post: requests.post,
    Methods.delete: requests.delete
}


def simple_request(method: Methods = Methods.get, path: str = '/', params: dict = None,
                   data: dict = None) -> requests.Response:
    data = json.dumps(data) if data is not None else data
    return map_methods[method](f'{PROTOCOL}://{HOST}:{PORT}{path}', params=params, data=data)


def imports(data: dict) -> requests.Response:
    return simple_request(Methods.post, '/imports', data=data)


def delete(id: str) -> requests.Response:
    return simple_request(Methods.delete, f'/delete/{id}')


def nodes(id: str) -> requests.Response:
    return simple_request(Methods.get, f'/nodes/{id}')


def sales(date: str) -> requests.Response:
    return simple_request(Methods.get, '/sales', params={'date': date})


def statistics(id: str, date_start: str = None, date_end: str = None) -> requests.Response:
    return simple_request(Methods.get, f'/node/{id}/statistic', params={'dateStart': date_start, 'dateEnd': date_end})


base_item = {
    'id': '3fa85f64-5717-4562-b3fc-000000000001',
    'name': f'Товар 1',
    'parentId': None,
    'type': 'OFFER',
    'price': 100
}

ERRS = {'validation': {'code': 400, 'message': 'Validation Failed'},
        'item_not_found': {'code': 404, 'message': 'Item not found'},
        }

ROOT = '3fa85f64-5717-4562-b3fc-000000000001'

# Категория 1:
# - Товар 1
# - Категория 1.1:
# - - Товар 2
# - - Товар 3
# - - Категория 1.2:
# - - - Товар 4

BASE_DATA = {
    'items': [
        {
            'id': ROOT,
            'name': f'Категория 1',
            'type': 'CATEGORY'
        },
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000002',
            'name': f'Категория 1.1',
            'parentId': ROOT,
            'type': 'CATEGORY'
        },
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000003',
            'name': f'Категория 1.2',
            'parentId': '3fa85f64-5717-4562-b3fc-000000000002',
            'type': 'CATEGORY'
        },
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000004',
            'name': f'Товар 1',
            'parentId': ROOT,
            'type': 'OFFER',
            'price': 50
        },
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000005',
            'name': f'Товар 2',
            'parentId': '3fa85f64-5717-4562-b3fc-000000000002',
            'type': 'OFFER',
            'price': 100
        },
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000006',
            'name': f'Товар 3',
            'parentId': '3fa85f64-5717-4562-b3fc-000000000002',
            'type': 'OFFER',
            'price': 300
        },
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000007',
            'name': f'Товар 4',
            'parentId': '3fa85f64-5717-4562-b3fc-000000000003',
            'type': 'OFFER',
            'price': 150
        },
    ],
    'updateDate': '2022-01-01T08:00:00.000Z'}

BASE_DATA_NODES = {
    'id': ROOT,
    'name': f'Категория 1',
    'parentId': None,
    'type': 'CATEGORY',
    'price': 150,
    'date': '2022-01-01T08:00:00.000Z',
    'children': [
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000004',
            'name': f'Товар 1',
            'parentId': ROOT,
            'type': 'OFFER',
            'price': 50,
            'date': '2022-01-01T08:00:00.000Z',
            'children': None,
        },
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000002',
            'name': f'Категория 1.1',
            'parentId': ROOT,
            'type': 'CATEGORY',
            'price': 183,
            'date': '2022-01-01T08:00:00.000Z',
            'children': [
                {
                    'id': '3fa85f64-5717-4562-b3fc-000000000005',
                    'name': f'Товар 2',
                    'parentId': '3fa85f64-5717-4562-b3fc-000000000002',
                    'type': 'OFFER',
                    'price': 100,
                    'date': '2022-01-01T08:00:00.000Z',
                    'children': None
                },
                {
                    'id': '3fa85f64-5717-4562-b3fc-000000000006',
                    'name': f'Товар 3',
                    'parentId': '3fa85f64-5717-4562-b3fc-000000000002',
                    'type': 'OFFER',
                    'price': 300,
                    'date': '2022-01-01T08:00:00.000Z',
                    'children': None
                },
                {
                    'id': '3fa85f64-5717-4562-b3fc-000000000003',
                    'name': f'Категория 1.2',
                    'parentId': '3fa85f64-5717-4562-b3fc-000000000002',
                    'type': 'CATEGORY',
                    'price': 150,
                    'date': '2022-01-01T08:00:00.000Z',
                    'children': [
                        {
                            'id': '3fa85f64-5717-4562-b3fc-000000000007',
                            'name': f'Товар 4',
                            'parentId': '3fa85f64-5717-4562-b3fc-000000000003',
                            'type': 'OFFER',
                            'price': 150,
                            'date': '2022-01-01T08:00:00.000Z',
                            'children': None
                        }
                    ]
                }
            ]
        }
    ]
}

BASE_DATA_NODES_AFTER_DEL = {
    'id': ROOT,
    'name': f'Категория 1',
    'parentId': None,
    'type': 'CATEGORY',
    'price': 150,
    'date': '2022-01-01T08:00:00.000Z',
    'children': [
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000004',
            'name': f'Товар 1',
            'parentId': ROOT,
            'type': 'OFFER',
            'price': 50,
            'date': '2022-01-01T08:00:00.000Z',
            'children': None,
        },
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000002',
            'name': f'Категория 1.1',
            'parentId': ROOT,
            'type': 'CATEGORY',
            'price': 200,
            'date': '2022-01-01T08:00:00.000Z',
            'children': [
                {
                    'id': '3fa85f64-5717-4562-b3fc-000000000005',
                    'name': f'Товар 2',
                    'parentId': '3fa85f64-5717-4562-b3fc-000000000002',
                    'type': 'OFFER',
                    'price': 100,
                    'date': '2022-01-01T08:00:00.000Z',
                    'children': None
                },
                {
                    'id': '3fa85f64-5717-4562-b3fc-000000000006',
                    'name': f'Товар 3',
                    'parentId': '3fa85f64-5717-4562-b3fc-000000000002',
                    'type': 'OFFER',
                    'price': 300,
                    'date': '2022-01-01T08:00:00.000Z',
                    'children': None
                }
            ]
        }
    ]
}

SOME_CHANGES = [
    {'items': [
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000004',
            'name': f'Товар 1',
            'parentId': ROOT,
            'type': 'OFFER',
            'price': 100
        }
    ],
        'updateDate': '2022-01-02T08:00:00.000Z'},
    {'items': [
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000004',
            'name': f'Товар 1',
            'parentId': ROOT,
            'type': 'OFFER',
            'price': 150
        }
    ],
        'updateDate': '2022-01-03T08:00:00.000Z'},
    {'items': [
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000004',
            'name': f'Товар 1',
            'parentId': ROOT,
            'type': 'OFFER',
            'price': 500
        }
    ],
        'updateDate': '2022-01-04T08:00:00.000Z'}
]

SALES = {
    'items':
    [
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000004',
            'name': 'Товар 1',
            'parentId': ROOT,
            'price': 150,
            'type': 'OFFER',
            'date': '2022-01-03T08:00:00.000Z'
        },
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000004',
            'name': 'Товар 1',
            'parentId': ROOT,
            'price': 100,
            'type': 'OFFER',
            'date': '2022-01-02T08:00:00.000Z'
        }
    ]
}

ROOT_STATS = {
    'items':
        [
            {
                'date': '2022-01-01T08:00:00.000Z',
                'id': '3fa85f64-5717-4562-b3fc-000000000001',
                'name': 'Категория 1',
                'parentId': None,
                'price': 150,
                'type': 'CATEGORY'
            },
            {
                'date': '2022-01-02T08:00:00.000Z',
                'id': '3fa85f64-5717-4562-b3fc-000000000001',
                'name': 'Категория 1',
                'parentId': None,
                'price': 166,
                'type': 'CATEGORY'
            },
            {
                'date': '2022-01-03T08:00:00.000Z',
                'id': '3fa85f64-5717-4562-b3fc-000000000001',
                'name': 'Категория 1',
                'parentId': None,
                'price': 183,
                'type': 'CATEGORY'
            },
            {
                'date': '2022-01-04T08:00:00.000Z',
                'id': '3fa85f64-5717-4562-b3fc-000000000001',
                'name': 'Категория 1',
                'parentId': None,
                'price': 300,
                'type': 'CATEGORY'}
        ]
}

SAME_IDS = {
    'items': [
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000002',
            'name': f'Товар 1',
            'type': 'OFFER',
            'price': 0
        },
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000002',
            'name': f'Товар 2',
            'type': 'OFFER',
            'price': 0
        }
    ],
    'updateDate': '2022-01-01T08:00:00.000Z'}

WRONG_PARENT = {
    'items': [
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000002',
            'name': f'Товар 1',
            'type': 'OFFER',
            'price': 0
        },
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000003',
            'name': f'Товар 2',
            'parentId': '3fa85f64-5717-4562-b3fc-000000000002',
            'type': 'OFFER',
            'price': 0
        }
    ],
    'updateDate': '2022-01-01T08:00:00.000Z'
}

NULL_NAME = {
    'items': [
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000002',
            'name': None,
            'type': 'OFFER',
            'price': 0
        }
    ],
    'updateDate': '2022-01-01T08:00:00.000Z'
}

NOT_NULL_CAT_PRICE = {
    'items': [
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000002',
            'name': 'Категория 1',
            'type': 'CATEGORY',
            'price': 99
        }
    ],
    'updateDate': '2022-01-01T08:00:00.000Z'
}

NULL_OFFER_PRICE = {
    'items': [
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000002',
            'name': 'Товар 1',
            'type': 'OFFER',
            'price': None
        }
    ],
    'updateDate': '2022-01-01T08:00:00.000Z'
}

NEGATIVE_OFFER_PRICE = {
    'items': [
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000002',
            'name': 'Товар 1',
            'type': 'OFFER',
            'price': -34
        }
    ],
    'updateDate': '2022-01-01T08:00:00.000Z'
}

WRONG_DATE = {
    'items': [
        {
            'id': '3fa85f64-5717-4562-b3fc-000000000002',
            'name': 'Товар 1',
            'type': 'OFFER',
            'price': 0
        }
    ],
    'updateDate': '2022-1-1TIME8:0:0.000Z'
}


class ColorsMeta(type):
    def __new__(cls, class_name, parents, attributes):
        for attr in attributes:
            if attr.startswith('_'): continue
            attributes[attr] = cls.__num_to_color(attributes[attr])
        return type(class_name, parents, attributes)

    @staticmethod
    def __num_to_color(num):
        return lambda x='': f'\033[{num}m{x}\033[m'


class CT(metaclass=ColorsMeta):
    red = 91
    green = 92
    yellow = 33
    blue = 34
    italic = 3


class test(object):
    methods = []

    def __init__(self, func):
        self._method = func
        self.__class__.methods.append(func)

    def __call__(self, *args, **kwargs):
        test_num = self.__class__.methods.index(self._method) + 1
        print(f'Test {test_num} {CT.yellow(self._method.__name__)}')
        if self._method.__doc__ is not None:
            print(f'{CT.italic(self._method.__doc__.strip())}')
        try:
            self._method()
        except AssertionError as ex:
            print(CT.red('Failed: ') + ''.join(ex.args))
            return
        else:
            print(CT.green('Passed'))
        finally:
            print()


@test
def test_same_ids():
    resp = imports(SAME_IDS)
    assert resp.json() == ERRS['validation'], 'Элементы с одинаковыми id не могут быть добавлены'


@test
def test_wrong_parent():
    resp = imports(WRONG_PARENT)
    assert resp.json() == ERRS['validation'], 'Родителем может быть только категория'


@test
def test_null_name():
    resp = imports(NULL_NAME)
    assert resp.json() == ERRS['validation'], 'Название элемента не может быть null'


@test
def test_wrong_cat_price():
    resp = imports(NOT_NULL_CAT_PRICE)
    assert resp.json() == ERRS['validation'], 'Цена у категорий должна быть null'


@test
def test_wrong_offer_price():
    resp = imports(NULL_OFFER_PRICE)
    assert resp.json() == ERRS['validation'], 'Цена у товара не может быть null'
    resp = imports(NEGATIVE_OFFER_PRICE)
    assert resp.json() == ERRS['validation'], 'Цена у товара не может быть отрицательной'


@test
def test_wrong_date():
    resp = imports(WRONG_DATE)
    assert resp.json() == ERRS['validation'], 'Дата должна быть в формате ISO8601'


@test
def test_imports():
    resp = imports(BASE_DATA)
    assert resp.status_code == 200, '/imports does not work =('


def deep_sort_children(node):
    if node.get("children"):
        node["children"].sort(key=lambda x: x["id"])

        for child in node["children"]:
            deep_sort_children(child)


@test
def test_nodes_and_avg_price():
    nodes_json = nodes(ROOT).json()
    deep_sort_children(nodes_json)
    deep_sort_children(BASE_DATA_NODES)
    assert nodes_json == BASE_DATA_NODES, 'Неправильный вывод /nodes'


@test
def test_delete():
    item = list(filter(lambda x: x['name'] == 'Категория 1.2', BASE_DATA['items']))[0]
    resp = delete(item['id'])
    assert resp.status_code == 200, '/delete does not work =('
    nodes_json = nodes(ROOT).json()
    deep_sort_children(nodes_json)
    deep_sort_children(BASE_DATA_NODES_AFTER_DEL)
    assert nodes_json == BASE_DATA_NODES_AFTER_DEL, \
        'Удаленный элемент и его дочерние не должны быть доступны, ' \
        'также должна обновиться цена родительских категорий'


@test
def test_sales():
    for data in SOME_CHANGES:
        imports(data)
    sales_json = sales('2022-01-03T08:00:00.000Z').json()
    SALES['items'].sort(key=lambda x: x['date'])
    sales_json['items'].sort(key=lambda x: x['date'])
    assert sales_json == SALES, '/sales does not work =('


@test
def test_statistics():
    stats_json = statistics(ROOT).json()
    stats_json['items'].sort(key=lambda x: x['date'])
    ROOT_STATS['items'].sort(key=lambda x: x['date'])
    assert stats_json == ROOT_STATS, '/statistic does not work =('


def main():
    test_imports()
    test_nodes_and_avg_price()
    test_delete()
    test_sales()
    test_statistics()

    # test_same_ids()
    # test_wrong_parent()
    # test_null_name()
    # test_wrong_cat_price()
    # test_wrong_offer_price()
    # test_wrong_date()
    delete(ROOT)


if __name__ == '__main__':
    main()
