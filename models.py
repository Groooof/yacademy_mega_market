from pydantic import BaseModel, UUID4, root_validator, NonNegativeInt
from enum import Enum
from typing import Optional, List
from datetime import datetime
from fastapi.exceptions import RequestValidationError
from pydantic import Field


UUID = UUID4
ID_FIELD = Field(description='Уникальный идентификатор', nullable=False, example='3fa85f64-5717-4562-b3fc-2c963f66a444')
NAME_FIELD = Field(description='Имя элемента', nullable=False, example='Элемент 1')
DATE_FIELD = Field(description='Время последнего обновления элемента', nullable=False, example='2022-05-28T21:12:01.000Z')
PARENTID_FIELD = Field(description='UUID родительской категории', nullable=True, example='3fa85f64-5717-4562-b3fc-2c963f66a333')
TYPE_FIELD = Field(description='Тип элемента - категория или товар', nullable=False)
PRICE_FIELD = Field(description='Целое число. Для категории - средняя цена всех дочерних товаров (включая товары подкатегорий). Если категория не содержит товаров - цена равна null. При импорте для категории всегда null.', nullable=True)
CHILDREN_FIELD = Field(description='Список всех дочерних товаров/категорий. Для товаров поле равно null.')
UPDATEDATE_FIELD = Field(description='Время обновления добавляемых товаров/категорий', nullable=False, example='2022-05-28T21:12:01.000Z')


def convert_datetime_to_iso_8601_with_z_suffix(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


class Tags(Enum):
    main = "Базовые задачи"
    additional = "Дополнительные задачи"


class ShopUnitType(str, Enum):
    """ Тип элемента - категория или товар """
    offer = 'OFFER'
    category = 'CATEGORY'


class ShopUnit(BaseModel):
    id: UUID = ID_FIELD
    name: str = NAME_FIELD
    date: datetime = DATE_FIELD
    parentId: Optional[UUID] = PARENTID_FIELD
    type: ShopUnitType = TYPE_FIELD
    price: Optional[NonNegativeInt] = PRICE_FIELD
    children: Optional[List['ShopUnit']] = CHILDREN_FIELD


class ShopUnitImport(BaseModel):
    id: UUID = ID_FIELD
    name: str = NAME_FIELD
    parentId: Optional[UUID] = PARENTID_FIELD
    type: ShopUnitType = TYPE_FIELD
    price: Optional[NonNegativeInt] = PRICE_FIELD

    @root_validator
    def price_validator(cls, values: dict):
        price = values.get('price')
        type = values.get('type')
        if type is ShopUnitType.offer and price is None:
            raise RequestValidationError
        if type is ShopUnitType.category and price is not None:
            raise RequestValidationError
        return values


class ShopUnitImportRequest(BaseModel):
    items: List[ShopUnitImport] = Field(description='Импортируемые элементы.', nullable=False)
    updateDate: datetime = UPDATEDATE_FIELD


class ShopUnitStatisticUnit(BaseModel):
    id: UUID = ID_FIELD
    name: str = NAME_FIELD
    parentId: Optional[UUID] = PARENTID_FIELD
    type: ShopUnitType = TYPE_FIELD
    price: Optional[NonNegativeInt] = PRICE_FIELD
    date: datetime = DATE_FIELD


class ShopUnitStatisticResponse(BaseModel):
    items: List[ShopUnitStatisticUnit] = Field(description='История в произвольном порядке.', nullable=False)

    class Config:
        json_encoders = {
            datetime: lambda x: x.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        }


class Error(BaseModel):
    code: int
    message: str
