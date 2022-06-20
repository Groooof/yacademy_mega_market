from typing import Union, Iterable, List
import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool
from abc import ABCMeta, abstractmethod
import models


class IDatabaseCore(metaclass=ABCMeta):
    @abstractmethod
    async def create_pool(self):
        """ Создает пул для дальнейшей работы с БД """

    @abstractmethod
    async def execute(self, command: str, args: Iterable = tuple(),
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False):
        """ Метод для выполнения запроса к БД """


class DatabaseCore(IDatabaseCore):
    def __init__(self):
        if not hasattr(self, 'pool'):
            self.pool: Union[Pool, None] = None

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(host='localhost', user='postgres', password='Biktimirov9', database='mega_market')

    async def execute(self, command: str, args=tuple(),
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False,
                      executemany: bool = False):
        result = None
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
                elif executemany:
                    result = await connection.executemany(command, args)
        return result


class MMDatabase(DatabaseCore):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    async def db_init(self):
        await self.create_extension_uuid_ossp()
        await self.create_enum_type()
        await self.create_main_table()
        await self.create_history_table()

        await self.create_function_history()
        await self.create_function_update_cat()
        await self.create_function_insert_in_cat()
        await self.create_function_delete_from_cat()
        await self.create_function_delete_cat()
        await self.create_function_get_avg_price()
        await self.create_function_check_errors()

        await self.create_trigger_history()
        await self.create_trigger_update_cat()
        await self.create_trigger_insert_in_cat()
        await self.create_trigger_delete_from_cat()
        await self.create_trigger_delete_cat()
        await self.create_trigger_check_errors()

    async def create_extension_uuid_ossp(self):
        command = '''CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'''
        await self.execute(command, execute=True)

    async def create_enum_type(self):
        command = '''
        DO
        $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'item_type') 
            THEN CREATE TYPE item_type AS ENUM ('OFFER', 'CATEGORY'); 
            END IF;
        END;
        $$
        LANGUAGE plpgsql;'''
        await self.execute(command, fetch=True)

    async def create_main_table(self):
        command = '''
        CREATE TABLE IF NOT EXISTS items (
            id uuid DEFAULT uuid_generate_v4(),
            name VARCHAR (255) NOT NULL,
            date TIMESTAMP with time zone NOT NULL,
            parentId uuid,
            type item_type NOT NULL,
            price INT,
            PRIMARY KEY (id)
        );
        '''
        await self.execute(command, execute=True)

    async def create_history_table(self):
        command = '''
                CREATE TABLE IF NOT EXISTS items_history (
                    id SERIAL,
                    item_id uuid,
                    item_name VARCHAR (255) NOT NULL,
                    item_date TIMESTAMP with time zone NOT NULL,
                    item_parentId uuid,
                    item_type item_type NOT NULL,
                    item_price INT,
                    PRIMARY KEY (id)
                );
                '''
        await self.execute(command, execute=True)

    async def create_trigger_history(self):
        command = '''
        CREATE OR REPLACE TRIGGER write_to_history_trigger 
        AFTER INSERT OR UPDATE ON items 
        FOR EACH ROW 
        EXECUTE FUNCTION write_to_history();
        '''
        await self.execute(command, execute=True)

    async def create_function_history(self):
        command = '''
        CREATE OR REPLACE FUNCTION write_to_history() 
        RETURNS trigger AS 
        $$
        BEGIN
            IF EXISTS (SELECT 1 FROM items_history WHERE item_id = NEW.id AND item_date = NEW.date) THEN 
                UPDATE items_history 
                SET (item_name, item_parentId, item_type, item_price) = (NEW.name, NEW.parentId, NEW.type, NEW.price) 
                WHERE item_id = NEW.id;
            ELSE  
                INSERT INTO items_history (item_id, item_name, item_date, item_parentId, item_type, item_price) 
                VALUES (NEW.id, NEW.name, NEW.date, NEW.parentId, NEW.type, NEW.price);
            END IF;
            RETURN NEW;
        END;
        $$
        LANGUAGE 'plpgsql';
        '''
        await self.execute(command, execute=True)

    async def create_trigger_update_cat(self):
        command = '''
        CREATE OR REPLACE TRIGGER update_cat 
        AFTER UPDATE ON items 
        FOR EACH ROW 
        EXECUTE FUNCTION update_cat_func();
        '''
        await self.execute(command, execute=True)

    async def create_trigger_insert_in_cat(self):
        command = '''
        CREATE OR REPLACE TRIGGER insert_in_cat 
        AFTER INSERT ON items 
        FOR EACH ROW 
        EXECUTE FUNCTION insert_in_cat_func();
        '''
        await self.execute(command, execute=True)

    async def create_trigger_delete_from_cat(self):
        command = '''
        CREATE OR REPLACE TRIGGER delete_from_cat 
        AFTER DELETE ON items 
        FOR EACH ROW 
        EXECUTE FUNCTION delete_from_cat_func();
        '''
        await self.execute(command, execute=True)

    async def create_trigger_delete_cat(self):
        command = '''
        CREATE OR REPLACE TRIGGER delete_cat 
        AFTER DELETE ON items 
        FOR EACH ROW 
        EXECUTE FUNCTION delete_cat_func();
        '''
        await self.execute(command, execute=True)

    async def create_trigger_check_errors(self):
        command = '''
                CREATE OR REPLACE TRIGGER check_errors  
                BEFORE INSERT OR UPDATE ON items 
                FOR EACH ROW 
                EXECUTE FUNCTION check_errors_func();
                '''
        await self.execute(command, execute=True)

    async def create_function_update_cat(self):
        command = '''
        CREATE OR REPLACE FUNCTION update_cat_func() 
        RETURNS trigger AS 
        $$
        BEGIN
            IF NEW.parentId != OLD.parentId THEN
                IF OLD.parentId IS NOT NULL THEN
                    UPDATE items SET date = NEW.date WHERE id = OLD.parentId;
                    UPDATE items SET price = (SELECT * FROM get_avg_price(OLD.parentId)) WHERE id = OLD.parentId;
                END IF;
                IF NEW.parentId IS NOT NULL THEN
                    UPDATE items SET date = NEW.date WHERE id = NEW.parentId;
                    UPDATE items SET price = (SELECT * FROM get_avg_price(NEW.parentId)) WHERE id = NEW.parentId;
                END IF;
            ELSIF OLD.parentId IS NOT NULL THEN
                UPDATE items SET date = NEW.date WHERE id = OLD.parentId;
                IF OLD.price != NEW.price THEN
                    UPDATE items SET price = (SELECT * FROM get_avg_price(OLD.parentId)) WHERE id = OLD.parentId;
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$
        LANGUAGE 'plpgsql';
        '''
        await self.execute(command, execute=True)

    async def create_function_insert_in_cat(self):
        command = '''
        CREATE OR REPLACE FUNCTION insert_in_cat_func() 
        RETURNS trigger AS 
        $$
        BEGIN
            IF NEW.parentId IS NOT NULL THEN
                UPDATE items SET date = NEW.date WHERE id = NEW.parentId;
                IF NEW.type = 'OFFER' THEN 
                    UPDATE items SET price = (SELECT * FROM get_avg_price(NEW.parentId) as avg) WHERE id = NEW.parentId;
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$
        LANGUAGE 'plpgsql';
        '''
        await self.execute(command, execute=True)

    async def create_function_delete_from_cat(self):
        command = '''
        CREATE OR REPLACE FUNCTION delete_from_cat_func() 
        RETURNS trigger AS 
        $$
        BEGIN
            IF OLD.parentId IS NOT NULL THEN
                UPDATE items SET price = (SELECT * FROM get_avg_price(OLD.parentId)) WHERE id = OLD.parentId;
            END IF;
            RETURN NEW;
        END;
        $$
        LANGUAGE 'plpgsql';
        '''
        await self.execute(command, execute=True)

    async def create_function_delete_cat(self):
        command = '''
        CREATE OR REPLACE FUNCTION delete_cat_func() 
        RETURNS trigger AS 
        $$
        BEGIN
            IF OLD.type = 'CATEGORY' THEN
                DELETE FROM items WHERE parentId = OLD.id;
                DELETE FROM items_history WHERE item_parentId = OLD.id OR item_id = OLD.id;
            END IF;
            RETURN NEW;
        END;
        $$
        LANGUAGE 'plpgsql';
        '''
        await self.execute(command, execute=True)

    async def create_function_get_avg_price(self):
        command = '''
        CREATE OR REPLACE FUNCTION get_avg_price(cat_id UUID) 
        RETURNS integer AS 
        $$
        BEGIN
            RETURN CAST(ROUND(AVG(price)-0.5) AS INT) FROM items 
                WHERE type = 'OFFER' AND parentId IN (
                    WITH RECURSIVE temp AS (
                        SELECT CAST($1 AS uuid) AS id
                    UNION
                        SELECT items.id FROM items JOIN temp ON (items.parentId = uuid(temp.id) AND type = 'CATEGORY')
                    ) 
                    SELECT * FROM temp);
        END;
        $$
        LANGUAGE 'plpgsql';
        '''
        await self.execute(command, execute=True)

    async def create_function_check_errors(self):
        command = '''
        CREATE OR REPLACE FUNCTION check_errors_func() 
        RETURNS trigger AS 
        $$
        BEGIN
            IF (SELECT type FROM items WHERE id = NEW.parentId) != 'CATEGORY' THEN
                RAISE EXCEPTION 'Родителем элемента может быть только категория!';
            END IF;
            IF TG_OP = 'UPDATE' THEN 
                IF OLD.type != NEW.type THEN 
                    RAISE EXCEPTION 'Тип элемента не может быть изменен!';
                END IF;
            END IF;
            
        RETURN NEW;
        END;
        $$
        LANGUAGE 'plpgsql';
        '''
        await self.execute(command, execute=True)

    async def insert_items(self, items: List[tuple]):
        command = '''
        INSERT INTO items (id, name, date, parentId, type, price) 
        VALUES ($1, $2, $3, $4, $5, $6) 
        ON CONFLICT (id) DO UPDATE 
        SET (name, date, parentId, type, price) = ($2, $3, $4, $5, $6) 
        '''
        await self.execute(command, items, executemany=True)

    async def delete_item(self, uuid):
        command_1 = '''DELETE FROM items WHERE id = $1 or parentId = $1;'''
        command_2 = '''DELETE FROM items_history WHERE item_id = $1 OR item_parentId = $1;'''
        await self.execute(command_1, (uuid, ), execute=True)
        await self.execute(command_2, (uuid, ), execute=True)

    async def get_item(self, uuid):
        command = '''
        WITH RECURSIVE temp AS (
            SELECT *, children FROM items WHERE id = $1;
        UNION
            INSERT INTO temp 
            SELECT items.id FROM items JOIN temp ON (items.parentId = uuid(temp.id) AND type = 'CATEGORY')
        ) 
        SELECT * FROM temp);
        '''
        command = '''
        SELECT (SELECT name FROM items WHERE parentId = $1) as arr;
        
        '''
        return await self.execute(command, (uuid, ), fetch=True)

    async def get_avg_price(self, cat_id):
        command = '''
            SELECT CAST(ROUND(AVG(price)-0.5) AS INT) FROM items 
                WHERE type = 'OFFER' AND parentId IN (
                    WITH RECURSIVE temp AS (
                        SELECT CAST($1 AS uuid) AS id
                    UNION
                        SELECT items.id FROM items JOIN temp ON (items.parentId = uuid(temp.id) AND type = 'CATEGORY')
                    ) 
                    SELECT * FROM temp);
            '''
        return await self.execute(command, (cat_id,), fetchval=True)


# обновление даты категории
# удаление подкатегорий


async def main():
    from datetime import datetime
    from pprint import pprint
    from time import time
    db = MMDatabase()
    await db.create_pool()

    # res = await db.create_extension_uuid_ossp()
    # res = await db.execute('''SELECT * FROM pg_extension;''', fetch=True)
    # res = await db.execute('''SELECT uuid_generate_v4()''', fetch=True)
    # res = await db.create_main_table()
    # res = await db.create_enum_type()
    # command = ''''''
    # res = await db.execute(command, fetch=True)
    # res = await db.db_init()
    # datetime.strptime('2022-01-01T08:00:00.000Z', '%Y-%m-%dT%H:%M:%S')
    # data = {'name': 'Товар-1',
    #         'date': datetime.strptime('2022-01-01T08:00:00', '%Y-%m-%dT%H:%M:%S'),
    #         'parentId': None,
    #         'type': 'OFFER',
    #         'price': 100}
    command = '''
    DELETE FROM items_history;
    '''
    # res = await db.execute(command, execute=True)
    # res = await db.delete_item('3fa85f64-5717-4562-b3fc-2c963f66a999')
    # res = await db.update_cat_avg_prices()
    # res = await db.db_init()

    s = time()
    # res = await db.get_avg_price('3fa85f64-5717-4562-b3fc-000000000003')
    # await db.create_function_get_avg_price()
    # res = await db.execute(''' SELECT * FROM get_avg_price($1) as avg ''', ('3fa85f64-5717-4562-b3fc-000000000001',), fetch=True)
    res = await db.get_item('3fa85f64-5717-4562-b3fc-000000000001')
    # res = models.ShopUnitStatisticUnit(**res[0])
    pprint(res)
    print(time()-s)


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    '''
    IF NEW.parentId != OLD.parentId:
        IF OLD.parentId IS NOT NULL:
            UPDATE items SET date = NEW.date WHERE id = OLD.parentId;
            UPDATE items SET price = (SELECT AVG(price) FROM items WHERE parentId = OLD.parentId) WHERE id = OLD.parentId;
        IF NEW.parentId IS NOT NULL:
            UPDATE items SET date = NEW.date WHERE id = NEW.parentId;
            UPDATE items SET price = (SELECT AVG(price) FROM items WHERE parentId = NEW.parentId) WHERE id = NEW.parentId;
    ELIF OLD.parentId IS NOT NULL:
        UPDATE items SET date = NEW.date WHERE id = OLD.parentId;
        IF OLD.price != NEW.price:
            UPDATE items SET price = (SELECT AVG(price) FROM items WHERE parentId = OLD.parentId) WHERE id = OLD.parentId;
    '''

