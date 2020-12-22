import asyncio

from asyncpgsa import PG
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from .files_storage import files
from .schema import urls_table


class DataBase:

    def __init__(
        self,
        *,
        driver="postgresql",
        host="0.0.0.0",
        login="andrey",
        pwd="andrey",
        db="mydb",
        loop_=None
    ):
        sql_params = f"{driver}://{login}:{pwd}@{host}/{db}"

        if not loop_:
            loop_ = asyncio.get_event_loop()

        self.loop = loop_
        self.pg = PG()

        self.loop.run_until_complete(
            self.pg.init(
                sql_params,
                min_size=5,
                max_size=100
            )
        )

    async def save_to_db(self, url, title, html_file_name, *, parent):
        print(f"Save url: {url}")
        async with self.pg.transaction() as conn:

            insert_query = insert(urls_table).values(
                {
                    "url": url,
                    "title": title,
                    "html": html_file_name,
                    "parent": parent
                }
            )

            update_query = insert_query.on_conflict_do_update(
                constraint="urls_url_key",
                set_={
                    "title": title,
                    "html": await self._update_html(url, html_file_name, conn),
                    "parent": parent
                }
            )

            await conn.execute(update_query)

    async def get_from_db(self, *, parent, limit=10):
        async with self.pg.transaction() as conn:
            query = select(
                [urls_table.c.url, urls_table.c.title]
            ).where(
                urls_table.c.parent == parent
            ).limit(limit)

            for res in await conn.fetch(query):
                print(f"{res[0]}: \"{res[1]}\"")

    @staticmethod
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

