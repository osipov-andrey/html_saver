import argparse
import asyncio
import httpx
import os
import time
import functools

from bs4 import BeautifulSoup
from yarl import URL

from db import DataBase, drop_table, create_table


def timer(func):

    @functools.wraps(func)
    async def wrapper(*args_, **kwargs):
        start = time.perf_counter()
        await func(*args_, **kwargs)
        finish = time.perf_counter()
        print(finish - start)
    return wrapper


def not_retries(func):
    cache = set()

    @functools.wraps(func)
    async def wrapper(url, *args_):
        if url not in cache:
            cache.add(url)
            await func(url, *args_)
        return
    return wrapper


class SpiderCrawler:

    def __init__(self, start_url, database, depth):
        self.client = httpx.AsyncClient()
        self.url = URL(start_url)
        self.db = database
        self.depth = depth

    @timer
    async def get_data_from_url(self):
        calls = 0

        @not_retries
        async def load(url_: URL, level_):
            nonlocal calls
            calls += 1
            try:
                title, html_body, soup = await self._load_and_parse(url_)
            except TypeError:
                # Can't download
                return

            asyncio.ensure_future(self.db.save_to_db(
                url_, title, html_body, parent=self.url.human_repr())
            )

            if level_ >= self.depth:
                return

            refs = self._ref_generator(soup.findAll('a'))
            todos = [load(ref, level_ + 1) for ref in refs]
            await asyncio.gather(*todos)

        try:
            await load(self.url, 0)
        finally:
            print("CALLS: ", calls)
            await self.client.aclose()
            await self.db.pg.pool.close()

    async def _load_and_parse(self, url_: URL):
        try:
            res = await self.client.get(str(url_))
        except httpx.HTTPError:
            return
        except ValueError:
            return

        soup = BeautifulSoup(res, 'lxml')

        try:
            title = soup.title.text
        except AttributeError:
            title = None
        html_body = res.text

        return title, html_body, soup

    def _ref_generator(self, bs_result_set):

        for ref in bs_result_set:
            try:
                href = URL(ref.attrs['href'])

                if href.query_string:  # Without QS
                    continue

                if not href.is_absolute():
                    href = self.url.join(href)

                if href != self.url:
                    yield href
            except KeyError:
                continue


ENV_VAR_PREFIX = 'SPIDER_'


def from_env(var: str):
    var = ENV_VAR_PREFIX + var.upper()
    return os.getenv(var)


def create_db(args):
    db = DataBase(
        login=args.db_login,
        pwd=args.db_pwd,
        host=args.db_host,
        db=args.db_name,
    )
    return db


def main():

    def _get(args_):
        db = create_db(args_)
        db.loop.run_until_complete(db.get_from_db(
            parent=args_.url, limit=int(args_.n)
        ))

    def _load(args_):
        db = create_db(args_)
        spider = SpiderCrawler(args_.url, db, int(args_.depth))
        db.loop.run_until_complete(spider.get_data_from_url())

    def _db(args_):
        action = args_.action.lower().strip()
        action_args = (
            args_.db_login, args_.db_pwd, args_.db_host, args_.db_name
        )

        if action == "create":
            create_table(*action_args)
        elif action == "drop":
            drop_table(*action_args)
        else:
            raise ValueError("Unknown db action!")

    parser = argparse.ArgumentParser(prog="SPYDER",)
    parser.add_argument("--db_login", default=from_env("db_login"))
    parser.add_argument("--db_pwd", default=from_env("db_pwd"))
    parser.add_argument("--db_host", default=from_env("db_host"))
    parser.add_argument("--db_name", default=from_env("db_name"))

    subparsers = parser.add_subparsers(help="Operating mode")

    parser_get = subparsers.add_parser("get", help="Get URL from database")
    parser_get.add_argument("url", help="URL-address")
    parser_get.add_argument("-n", help="Number of URLs", default=5)
    parser_get.set_defaults(func=_get)

    parser_load = subparsers.add_parser("load", help="Load URL to database")
    parser_load.add_argument("url", help="URL-address")
    parser_load.add_argument("--depth", help="Depth of scraping for load",
                             default=1)
    parser_load.set_defaults(func=_load)

    parser_db = subparsers.add_parser("db", help="operation with database")
    parser_db.add_argument("action", help="drop/create")
    parser_db.set_defaults(func=_db)

    args = parser.parse_args()
    print(args)
    args.func(args)


if __name__ == '__main__':
    main()
