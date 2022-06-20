import asyncpg.exceptions
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import responses
import models
from fastapi import Path, Query
from database import MMDatabase
from random import randint
import openapi_editor
from pprint import pprint


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes
    )
    openapi_editor.del_response(openapi_schema, '422')
    openapi_editor.del_schema(openapi_schema, 'HTTPValidationError')
    openapi_editor.del_schema(openapi_schema, 'ValidationError')

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI(title="MegaMarket API", version="1.0.0", description="*by Biktimirov A.S.*",)
app.openapi = custom_openapi


@app.on_event('startup')
async def create_db_pool():
    db = MMDatabase()
    await db.create_pool()
    await db.db_init()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(content=models.Error(code=400, message='Validation Failed').dict(),
                        status_code=400)


@app.post('/imports', responses=responses.imports_responses, status_code=200, tags=[models.Tags.main])
async def imports(data: models.ShopUnitImportRequest = None):
    """ Импортирует новые товары и/или категории. Товары/категории импортированные повторно обновляют текущие. """

    db = MMDatabase()
    ids = list(map(lambda x: x.id, data.items))
    if len(ids) != len(set(ids)):
        raise RequestValidationError('Duplicate ids')

    prepared_items = list(map(lambda x: (x.id, x.name, data.updateDate, x.parentId, x.type, x.price), data.items))
    try:
        res = await db.insert_items(prepared_items)
    except asyncpg.exceptions.RaiseError as ex:
        raise RequestValidationError(ex.args[0])
    return res


@app.delete('/delete/{id}', responses=responses.delete_responses, tags=[models.Tags.main])
async def delete(id: models.UUID =
                 Path(description='Идентификатор', example='3fa85f64-5717-4562-b3fc-2c963f66a333')):
    """ Удалить элемент по идентификатору. При удалении категории удаляются все дочерние элементы. """

    db = MMDatabase()
    if not await db.item_exists(id):
        return JSONResponse(content=models.Error(code=404, message='Item not found').dict(), status_code=404)
    await db.delete_item(id)


@app.get('/nodes/{id}', responses=responses.nodes_responses, tags=[models.Tags.main])
async def nodes(id: models.UUID =
                Path(description='Идентификатор', example='3fa85f64-5717-4562-b3fc-2c963f66a333')):
    """ Получить информацию об элементе по идентификатору.
    При получении информации о категории также предоставляется информация о её дочерних элементах. """

    async def get_item_hierarchy(db_record):
        item = models.ShopUnit(**db_record, children=None)
        if item.type == models.ShopUnitType.offer:
            return item
        item.children = list()
        children = await db.get_item_children(item.id)
        for child in children:
            print(child)
            item.children.append(await get_item_hierarchy(child))
        return item

    db = MMDatabase()
    if not await db.item_exists(id):
        return JSONResponse(content=models.Error(code=404, message='Item not found').dict(), status_code=404)

    item = await db.get_item(id)
    item = await get_item_hierarchy(item)
    return item.dict()


@app.get('/sales', responses=responses.sales_responses, tags=[models.Tags.additional])
async def sales(date: models.datetime =
                Query(description='Дата и время запроса.', example='2022-05-28T21:12:01.000Z')):
    """ Получение списка товаров, цена которых была обновлена за последние 24 часа включительно. """

    db = MMDatabase()
    items = await db.get_last_24h(date)
    return models.ShopUnitStatisticResponse(items=items)


@app.get('/node/{id}/statistic', responses=responses.statistic_responses, tags=[models.Tags.additional])
async def statistics(id: models.UUID =
                     Path(description='UUID товара/категории для которой будет отображаться статистика',
                          example='3fa85f64-5717-4562-b3fc-2c963f66a333'),
                     dateStart: models.datetime =
                     Query(None, description='Дата и время начала интервала, для которого считается статистика.',
                           example='2022-05-28T21:12:01.000Z'),
                     dateEnd: models.datetime =
                     Query(None, description='Дата и время конца интервала, для которого считается статистика.',
                           example='2022-05-28T21:12:01.000Z')):
    """ Получение статистики (истории обновлений) по товару/категории за заданный полуинтервал [from, to).
    Статистика по удаленным элементам недоступна. """

    db = MMDatabase()
    if not await db.item_exists(id):
        return JSONResponse(content=models.Error(code=404, message='Item not found').dict(), status_code=404)

    items = await db.get_statistics(id, dateStart, dateEnd)
    return models.ShopUnitStatisticResponse(items=items)
