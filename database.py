from datetime import datetime
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
        env = models.EnvSettings()
        self.pool = await asyncpg.create_pool(host=env.postgres_host, port=env.postgres_port, user=env.postgres_user, password=env.postgres_password, database=env.postgres_db)

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
            "parentId" uuid,
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
                    "item_parentId" uuid,
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
                SET (item_name, "item_parentId", item_type, item_price) = (NEW.name, NEW."parentId", NEW.type, NEW.price) 
                WHERE item_id = NEW.id;
            ELSE  
                INSERT INTO items_history (item_id, item_name, item_date, "item_parentId", item_type, item_price) 
                VALUES (NEW.id, NEW.name, NEW.date, NEW."parentId", NEW.type, NEW.price);
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
            IF (NEW.type = 'CATEGORY') AND (NEW.price IS NULL) AND (OLD.price IS NOT NULL) AND (EXISTS (SELECT 1 FROM items WHERE "parentId" = NEW.id)) THEN
                UPDATE items SET price = OLD.price WHERE id = NEW.id;
            END IF;
            
            IF NEW."parentId" = OLD."parentId" THEN
                UPDATE items SET date = NEW.date WHERE id = OLD."parentId";
                IF OLD.price = NEW.price THEN
                    RETURN NEW;
                END IF;
                UPDATE items SET price = (SELECT * FROM get_avg_price(OLD."parentId")) WHERE id = OLD."parentId";
            ELSE 
                IF OLD."parentId" IS NOT NULL THEN
                    UPDATE items SET date = NEW.date WHERE id = OLD."parentId";
                    UPDATE items SET price = (SELECT * FROM get_avg_price(OLD."parentId")) WHERE id = OLD."parentId";
                END IF;
                IF NEW."parentId" IS NOT NULL THEN
                    UPDATE items SET date = NEW.date WHERE id = NEW."parentId";
                    UPDATE items SET price = (SELECT * FROM get_avg_price(NEW."parentId")) WHERE id = NEW."parentId";
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
            IF NEW."parentId" IS NOT NULL THEN
                UPDATE items SET date = NEW.date WHERE id = NEW."parentId";
                IF NEW.type = 'OFFER' THEN 
                    UPDATE items SET price = (SELECT * FROM get_avg_price(NEW."parentId") as avg) WHERE id = NEW."parentId";
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
            IF OLD."parentId" IS NOT NULL THEN
                UPDATE items SET price = (SELECT * FROM get_avg_price(OLD."parentId")) WHERE id = OLD."parentId";
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
            DELETE FROM items_history WHERE item_id = OLD.id;
            IF OLD.type = 'CATEGORY' THEN
                DELETE FROM items WHERE "parentId" = OLD.id;
                DELETE FROM items_history WHERE "item_parentId" = OLD.id;
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
                WHERE type = 'OFFER' AND "parentId" IN (
                    WITH RECURSIVE temp AS (
                        SELECT CAST($1 AS uuid) AS id
                    UNION
                        SELECT items.id FROM items JOIN temp ON (items."parentId" = uuid(temp.id) AND type = 'CATEGORY')
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
            IF (SELECT type FROM items WHERE id = NEW."parentId") != 'CATEGORY' THEN
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
        INSERT INTO items (id, name, date, "parentId", type, price) 
        VALUES ($1, $2, $3, $4, $5, $6) 
        ON CONFLICT (id) DO UPDATE 
        SET (name, date, "parentId", type, price) = ($2, $3, $4, $5, $6) 
        '''
        await self.execute(command, items, executemany=True)

    async def delete_item(self, uuid):
        command = '''DELETE FROM items WHERE id = $1 or "parentId" = $1 IS TRUE RETURNING 1;'''
        await self.execute(command, (uuid, ), execute=True)

    async def get_item(self, uuid):
        command = '''SELECT * FROM items WHERE id = $1;'''
        return await self.execute(command, (uuid, ), fetchrow=True)

    async def get_item_children(self, uuid):
        command = '''SELECT * FROM items WHERE "parentId" = $1;'''
        return await self.execute(command, (uuid, ), fetch=True)

    async def get_avg_price(self, cat_id):
        command = '''
            SELECT CAST(ROUND(AVG(price)-0.5) AS INT) FROM items 
                WHERE type = 'OFFER' AND "parentId" IN (
                    WITH RECURSIVE temp AS (
                        SELECT CAST($1 AS uuid) AS id
                    UNION
                        SELECT items.id FROM items JOIN temp ON (items."parentId" = uuid(temp.id) AND type = 'CATEGORY')
                    ) 
                    SELECT * FROM temp);
            '''
        return await self.execute(command, (cat_id,), fetchval=True)

    async def get_last_24h(self, date):
        command = '''
        SELECT item_id as id, item_name as name, item_date as date, "item_parentId" as "parentId", item_type as type, item_price as price  
        FROM items_history WHERE item_type = 'OFFER' AND item_date <= $1 AND item_date >= $1 - INTERVAL '24 hour';
        '''
        return await self.execute(command, (date,), fetch=True)

    async def get_statistics(self, uuid, date_start, date_end):
        if date_start is None: date_start = datetime(1971, 1, 1, 0, 0)
        if date_end is None: date_end = datetime(3000, 1, 1, 0, 0)
        command = '''
        SELECT item_id as id, item_name as name, item_date as date, "item_parentId" as "parentId", item_type as type, item_price as price   
        FROM items_history 
        WHERE 
            item_id = $1 AND
            item_date >= $2 AND
            item_date < $3;
        '''
        return await self.execute(command, (uuid, date_start, date_end), fetch=True)

    async def item_exists(self, uuid):
        command = '''SELECT EXISTS(SELECT id FROM items WHERE id = $1);'''
        return await self.execute(command, (uuid, ), fetchval=True)


async def main():
    from datetime import datetime
    from pprint import pprint
    from time import time
    db = MMDatabase()
    await db.create_pool()


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
