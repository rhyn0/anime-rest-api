#! /usr/bin/env python3
import argparse
import asyncio
import sys

from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy.ext.asyncio import AsyncConnection

from anime_rest_api.db import DatabaseConnection
from anime_rest_api.db import DB_METADATA, setup_db


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("setup_db")
    parser.add_argument("database_url", metavar="<URL>")
    return parser.parse_args()

async def clean_db(conn: AsyncConnection) -> None:
    await conn.run_sync(DB_METADATA.drop_all)
    await conn.execute(DropSchema(DB_METADATA.schema, cascade=True))


async def main(args: argparse.Namespace) -> int:
    dbc = DatabaseConnection(args.database_url, echo=True)
    async with dbc.engine.begin() as conn:
        await clean_db(conn)
        await setup_db(conn)
    return 0


if __name__ == "__main__":
    args = get_args()
    sys.exit(asyncio.run(main(args)))
