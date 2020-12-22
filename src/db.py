import asyncio

from asyncpgsa import PG
from sqlalchemy import (Column, String, Text, Table, Integer,
                        MetaData, create_engine, UniqueConstraint, select)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.declarative import declarative_base

import files


Base = declarative_base()



loop = asyncio.get_event_loop()


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
urls_table.create(engine, checkfirst=True)

def refresh_table():
    urls_table.drop(engine)
    urls_table.create(engine)
    files.drop_html_files()


async def save_to_db(url, title, html_file_name, *, parent):
    print(f"Save url: {url}")
    async with pg.transaction() as conn:

        data = {
            "url": url,
            "title": title,
            "html": html_file_name,
            "parent": parent
        }

        insert_query = insert(urls_table).values(
            **data
        )

        update_query = insert_query.on_conflict_do_update(
            constraint="urls_url_key",
            set_={
                "title": title,
                "html": await _update_html(url, html_file_name, conn),
                "parent": parent
            }
        )

        await conn.execute(update_query)


async def _update_html(url: str, html_file_name: str, connection):
    """ Удалять HTML-файлы, ссылки на которые удаляются из БД """

    query = select(
        [urls_table.c.html, ]
    ).where(
        urls_table.c.url == url
    )

    old_html = await connection.fetchval(query)

    if old_html:
        files.del_html(old_html)
        print("Delete file: ", old_html)

    return html_file_name


async def get_from_db(*, parent, limit=10):
    async with pg.transaction() as conn:
        for res in await conn.fetch(
            SELECT_QUERY,
            parent, limit
        ):
            print(f"{res[0]}: \"{res[1]}\"")
