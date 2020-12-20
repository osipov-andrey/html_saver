import asyncio

from asyncpgsa import PG
from sqlalchemy import (Column, String, Text, Table, Integer,
                        MetaData, create_engine, UniqueConstraint)
from sqlalchemy.dialects.postgresql import insert
import files

loop = asyncio.get_event_loop()

CREATE_QUERY = "INSERT INTO urls(url, title, html, parent)" \
               "VALUES($1, $2, $3, $4)"

SELECT_QUERY = "SELECT url, title FROM urls " \
               "WHERE parent = $1 LIMIT $2"
# Base = declarative_base()
metadata = MetaData()
urls_table = Table(
    # TODO декларативная модель, session query, удалять файлы при апдейте
    'urls',
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column('url', String, nullable=False, unique=True),
    Column('title', Text, onupdate=True),
    Column('parent', String, nullable=False),
    Column('html', Text),
    # UniqueConstraint("url", "title", name="url_title")
)

engine = create_engine(
    'postgresql://andrey:andrey@0.0.0.0/mydb', echo=True
)

pg = PG()
loop.run_until_complete(
    pg.init(
        'postgresql://andrey:andrey@0.0.0.0/mydb',
        loop=loop,
        min_size=5,
        max_size=100
    )
)


def refresh_table():
    urls_table.drop(engine)
    urls_table.create(engine)
    files.drop_html_files()


async def save_to_db(url, title, html, *, parent):
    print(f"Save url: {url}")
    async with pg.transaction() as conn:
        # await conn.execute(
        #     CREATE_QUERY,
        #     url, title, html, parent
        # )

        data = {
            "url": url,
            "title": title,
            "html": html,
            "parent": parent
        }

        insert_query = insert(urls_table).values(
            **data
        )

        update_query = insert_query.on_conflict_do_update(
            constraint="urls_url_key",
            # index_elements=["id"],
            set_={
                "title": title,
                "html": html,
                "parent": parent
            }
        )

        await conn.execute(update_query)


async def get_from_db(*, parent, limit=10):
    async with pg.transaction() as conn:
        for res in await conn.fetch(
            SELECT_QUERY,
            parent, limit
        ):
            print(f"{res[0]}: \"{res[1]}\"")
