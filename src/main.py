import argparse
import asyncio
import httpx

from bs4 import BeautifulSoup
from yarl import URL

from html_saver.src.db import db
from html_saver.src.db.db import files


def ref_generator(root_url: str, bs_result_set):
    root = URL(root_url)
    for ref in bs_result_set:
        try:
            href = URL(ref.attrs['href'])

            if href.query_string:  # Without QS
                continue

            if not href.is_absolute():
                href = root.join(href)

            if href != root:
                yield href
        except KeyError:
            continue


async def get_data_from_url(url: str, load_level):

    client = httpx.AsyncClient()

    async def load(url_, level_):

        try:
            res = await client.get(str(url_))
        except httpx.HTTPError:
            return
        except ValueError:
            return

        soup = BeautifulSoup(res, 'lxml')

        try:
            title = soup.title.text
        except AttributeError:
            title = None
        html = res.text

        html = await files.save_html(url_, html)
        asyncio.ensure_future(db.save_to_db(str(url_), title, html, parent=url), loop=db.loop)

        if level_ >= load_level:
            return
        refs = {*ref_generator(url, soup.findAll('a'))}
        todos = [load(ref, level_ + 1) for ref in refs]
        await asyncio.gather(*todos, loop=db.loop)

    try:
        await load(URL(url), 0)
    finally:
        await client.aclose()
        await db.pg.pool.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", help="load/get/drop")
    parser.add_argument("--url", help="URL-address", default=None)

    parser.add_argument("--depth", help="Depth of scraping for load", default=2)
    parser.add_argument("-n", help="Rows count to get", default=10)

    args = parser.parse_args()

    cmd = args.cmd.lower().strip()

    if cmd == "load":
        db.loop.run_until_complete(get_data_from_url(
            args.url, int(args.depth)
        ))
    elif cmd == "get":
        db.loop.run_until_complete(db.get_from_db(
            parent=args.url, limit=int(args.n)
        ))
    elif cmd == "drop":
        db.refresh_table()
