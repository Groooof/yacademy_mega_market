from enum import Enum
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import responses
import models
from fastapi import Path, Query
from main import app
from database import db
from random import randint


class Tags(Enum):
    main = "Базовые задачи"
    additional = "Дополнительные задачи"


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(content=models.Error(code=400, message='Validation Failed').dict(),
                        status_code=400)


@app.post('/imports', responses=responses.imports_responses, status_code=200, tags=[Tags.main])
async def imports(data: models.ShopUnitImportRequest = None):
    """ Импортирует новые товары и/или категории. Товары/категории импортированные повторно обновляют текущие. """

    res = await db.execute('''INSERT INTO test(name) VALUES($1);''', ('Name-' + randint(0, 99)), fetch=True)

    return res


@app.delete('/delete/{id}', responses=responses.delete_responses, tags=[Tags.main])
async def delete(id: models.UUID = Path(description='Идентификатор', example='3fa85f64-5717-4562-b3fc-2c963f66a333')):
    """ Удалить элемент по идентификатору. При удалении категории удаляются все дочерние элементы. """

    return {'msg': 'This is delete endpoint'}


@app.get('/nodes/{id}', responses=responses.nodes_responses, tags=[Tags.main])
async def nodes(id: models.UUID = Path(description='Идентификатор', example='3fa85f64-5717-4562-b3fc-2c963f66a333')):
    """ Получить информацию об элементе по идентификатору.
    При получении информации о категории также предоставляется информация о её дочерних элементах. """

    return {'msg': 'This is nodes endpoint'}


@app.get('/sales', responses=responses.sales_responses, tags=[Tags.additional])
async def sales(date: models.datetime = Query(description='Дата и время запроса.', example='2022-05-28T21:12:01.000Z')):
    """ Получение списка товаров, цена которых была обновлена за последние 24 часа включительно. """

    return {'msg': 'This is sales endpoint'}


@app.get('/node/{id}/statistic', responses=responses.statistic_responses, tags=[Tags.additional])
async def statistics(id: models.UUID = Path(description='UUID товара/категории для которой будет отображаться статистика', example='3fa85f64-5717-4562-b3fc-2c963f66a333'),
               dateStart: models.datetime = Query(None, description='Дата и время начала интервала, для которого считается статистика.', example='2022-05-28T21:12:01.000Z'),
               dateEnd: models.datetime = Query(None, description='Дата и время конца интервала, для которого считается статистика.', example='2022-05-28T21:12:01.000Z'),
               ):
    """ Получение статистики (истории обновлений) по товару/категории за заданный полуинтервал [from, to).
    Статистика по удаленным элементам недоступна. """

    return {'msg': 'This is statistic endpoint'}

