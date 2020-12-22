from sqlalchemy import (Column, String, Text, Table, Integer, MetaData, )


metadata = MetaData()

urls_table = Table(
    'urls',
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column('url', String, nullable=False, unique=True),
    Column('title', Text, onupdate=True),
    Column('parent', String, nullable=False),
    Column('html', Text),
)
