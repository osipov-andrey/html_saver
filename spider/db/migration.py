from sqlalchemy import create_engine

from . import schema
from .files_storage import files


def _engine(login, pwd, host, db):
    return create_engine(f'postgresql://{login}:{pwd}@{host}/{db}', echo=True)


def drop_table(login, pwd, host, db):
    engine = _engine(login, pwd, host, db)
    schema.urls_table.drop(engine)
    schema.urls_table.create(engine)
    files.drop_html_files()


def create_table(login, pwd, host, db):
    engine = _engine(login, pwd, host, db)
    schema.urls_table.create(engine, checkfirst=True)
