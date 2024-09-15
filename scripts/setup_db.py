#! /usr/bin/env python3
import argparse
import asyncio
import sys

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.schema import CreateSchema

from anime_rest_api.db.models import DB_METADATA


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("setup_db")
    parser.add_argument("database_url", metavar="<URL>")
    return parser.parse_args()


async def main(args: argparse.Namespace) -> int:
    engine = create_async_engine(args.database_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(DB_METADATA.drop_all)
        await conn.execute(CreateSchema(DB_METADATA.schema))
        await conn.run_sync(DB_METADATA.create_all)
    return 0


if __name__ == "__main__":
    args = get_args()
    sys.exit(asyncio.run(main(args)))
