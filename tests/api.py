import requests
from enum import Enum
import json

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
