import argparse

from sqlalchemy import create_engine

import schema
from files_storage import files


def drop(engine):
    schema.urls_table.drop(engine)
    schema.urls_table.create(engine)
    files.drop_html_files()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", help="create/drop table")
    parser.add_argument("--db", help="Database type", default="postgresql")
    parser.add_argument("--db_params", help="Database params",
                        default="andrey:andrey@0.0.0.0/mydb")
    args = parser.parse_args()

    cmd = args.cmd.lower().strip()
    db = args.db
    db_params = args.db_params

    engine = create_engine(f'{db}://{db_params}', echo=True)

    if cmd == "create":
        schema.urls_table.create(engine, checkfirst=True)
    elif cmd == "drop":
        drop(engine)
    else:
        raise ValueError("Unknown cmd!")


if __name__ == '__main__':
    main()
