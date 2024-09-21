#! /usr/bin/env python3
import argparse
import asyncio
import os
import sys

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("setup_db")
    parser.add_argument("database_url", metavar="<URL>")
    return parser.parse_args()


def main(args: argparse.Namespace) -> int:
    os.environ["ANIME_API_DATABASE_URL"] = args.database_url
    from anime_rest_api.db import DatabaseConnection
    from anime_rest_api.db import setup_db, clean_db
    async def _db_calls(dbc: "DatabaseConnection") -> None:
        async with dbc.engine.begin() as conn:
            await clean_db(conn)
            await setup_db(conn)
    del DatabaseConnection._instance
    dbc = DatabaseConnection(args.database_url, echo=True)
    asyncio.run(_db_calls(dbc))
    return 0


if __name__ == "__main__":
    args = get_args()
    sys.exit(main(args))
