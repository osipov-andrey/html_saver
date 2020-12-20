import uuid

from aiofile import AIOFile, Writer
from pathlib import Path
import os
from yarl import URL


PATH_TO_FILES = Path(__file__).parent.absolute().joinpath("html_files")


async def save_html(url_: URL, html: str) -> str:
    file_name = f"{url_.host.replace('.', '_')}_{uuid.uuid4()}.html"
    path = PATH_TO_FILES.joinpath(file_name)
    async with AIOFile(path, "w") as f:
        writer = Writer(f)
        await writer(html)
    return str(path)


def del_html(file_name):
    os.remove(PATH_TO_FILES.joinpath(file_name))


def drop_html_files():
    for file in os.listdir(PATH_TO_FILES):
        del_html(file)

