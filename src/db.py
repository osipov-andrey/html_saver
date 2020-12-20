import asyncio

from asyncpgsa import PG
from sqlalchemy import Column, String, Text, Table, MetaData, create_engine, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


loop = asyncio.get_event_loop()

CREATE_QUERY = "INSERT INTO urls(url, title, html, parent)" \
               "VALUES($1, $2, $3, $4)"

SELECT_QUERY = "SELECT url, title FROM urls " \
               "WHERE parent = $1 LIMIT $2"

metadata = MetaData()
urls_table = Table(
    'urls',
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column('url', String, nullable=False),
    Column('title', Text),
    Column('parent', String, nullable=False),
    Column('html', Text)
)


engine = create_engine(
    'postgresql://andrey:andrey@0.0.0.0/mydb', echo=True
)
# urls_table.drop(engine)
# urls_table.create(engine)


pg = PG()
loop.run_until_complete(
        pg.init(
            'postgresql://andrey:andrey@0.0.0.0/mydb',
            loop=loop,
            min_size=5,
            max_size=100
    )
)


async def save_to_db(url, title, html=None, *, parent):
    print(f"Save url: {url}")
    async with pg.transaction() as conn:
        await conn.execute(
            CREATE_QUERY,
            url, title, html, parent
        )
        # query = urls_table.insert()
        # await conn.execute(query.values(url=url, title=title))


async def get_from_db(*, parent, limit=10):
    async with pg.transaction() as conn:
        for res in await conn.fetch(
            SELECT_QUERY,
            parent, limit
        ):
            print(f"{res[0]}: \"{res[1]}\"")


if __name__ == '__main__':

    try:
        loop.run_until_complete(save_to_db())
    finally:
        loop.run_until_complete(pg.pool.close())


