import argparse
import asyncio
import functools
import time

import httpx

from bs4 import BeautifulSoup
from yarl import URL

from db import DataBase


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", help="load/get")
    parser.add_argument("url", help="URL-address")

    parser.add_argument("--depth", help="Depth of scraping for load", default=2)
    parser.add_argument("-n", help="Rows count to get", default=10)

    args = parser.parse_args()

    cmd = args.cmd.lower().strip()

    db = DataBase()

    if cmd == "load":
        spider = SpiderCrawler(args.url, db, int(args.depth))

        db.loop.run_until_complete(spider.get_data_from_url())

    elif cmd == "get":
        db.loop.run_until_complete(db.get_from_db(
            parent=args.url, limit=int(args.n)
        ))


if __name__ == '__main__':
    main()
