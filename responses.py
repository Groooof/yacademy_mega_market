import models
from models import Error

default400 = {
    400: {
        "model": Error,
        "description": "Невалидная схема документа или входные данные не верны.",
        "content": {
            "application/json": {
                "example": Error(code=400, message='Validation Failed'),
            }
        }
    }
}

default404 = {
    404: {
        "model": Error,
        "description": "Категория/товар не найден.",
        "content": {
            "application/json": {
                "example": Error(code=404, message='Item not found'),
            }
        }
    }
}

imports_responses = {
    **default400,
    200: {
            "description": "Вставка или обновление прошли успешно.",
            "content": None
    },

}

delete_responses = {
    **default400,
    **default404,
    200: {
            "description": "Удаление прошло успешно.",
            "content": None
    },
}

nodes_responses = {
    **default400,
    **default404,
    200: {
            "model": models.ShopUnit,
            "description": "Информация об элементе.",
            # "content": {
            #     "application/json": {
            #         "example": {
            #               "id": "3fa85f64-5717-4562-b3fc-2c963f66a111",
            #               "name": "Категория",
            #               "type": "CATEGORY",
            #               "parentId": 'null',
            #               "date": "2022-05-28T21:12:01.000Z",
            #               "price": 6,
            #               "children": [
            #                 {
            #                   "name": "Оффер 1",
            #                   "id": "3fa85f64-5717-4562-b3fc-2c963f66a222",
            #                   "price": 4,
            #                   "date": "2022-05-28T21:12:01.000Z",
            #                   "type": "OFFER",
            #                   "parentId": "3fa85f64-5717-4562-b3fc-2c963f66a111"
            #                 },
            #                 {
            #                   "name": "Подкатегория",
            #                   "type": "CATEGORY",
            #                   "id": "3fa85f64-5717-4562-b3fc-2c963f66a333",
            #                   "date": "2022-05-26T21:12:01.000Z",
            #                   "parentId": "3fa85f64-5717-4562-b3fc-2c963f66a111",
            #                   "price": 8,
            #                   "children": [
            #                     {
            #                       "name": "Оффер 2",
            #                       "id": "3fa85f64-5717-4562-b3fc-2c963f66a444",
            #                       "parentId": "3fa85f64-5717-4562-b3fc-2c963f66a333",
            #                       "date": "2022-05-26T21:12:01.000Z",
            #                       "price": 8,
            #                       "type": "OFFER"
            #                     }
            #                   ]
            #                 }
            #               ]
            #             },
            #     }
            # }
    },
}

sales_responses = {
    **default400,
    200: {
            "model": models.ShopUnitStatisticResponse,
            "description": "Список товаров, цена которых была обновлена.",
            # "content": {
            #     "application/json": {
            #         "example": {
            #               "items": [
            #                 {
            #                   "id": "3fa85f64-5717-4562-b3fc-2c963f66a444",
            #                   "name": "Оффер",
            #                   "date": "2022-05-28T21:12:01.000Z",
            #                   "parentId": "3fa85f64-5717-4562-b3fc-2c963f66a333",
            #                   "price": 234,
            #                   "type": "OFFER"
            #                 }
            #               ]
            #             },
            #     }
            # }
    }
}

statistic_responses = {
    **default404,
    200: {
            "model": models.ShopUnitStatisticResponse,
            "description": "Статистика по элементу.",
            # "content": {
            #     "items": [
            #         {
            #           "id": "3fa85f64-5717-4562-b3fc-2c963f66a444",
            #           "name": "Оффер",
            #           "date": "2022-05-28T21:12:01.000Z",
            #           "parentId": "3fa85f64-5717-4562-b3fc-2c963f66a333",
            #           "price": 234,
            #           "type": "OFFER"
            #         }
            #       ]
            #     }
    },
    400: {
        "description": "Некорректный формат запроса или некорректные даты интервала.",
        "content": {
            "application/json": {
                "example": Error(code=400, message='Validation Failed'),
            }
        }
    },
}
