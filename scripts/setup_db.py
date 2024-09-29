#! /usr/bin/env python3
import argparse
import asyncio
import os
import sys

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncConnection

from anime_rest_api.db import DatabaseConnection
from anime_rest_api.db import setup_db, clean_db
from anime_rest_api.db.crud.user_operations import password_salt_hash_statement
from anime_rest_api.db.models.auth import User

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("setup_db")
    parser.add_argument("database_url", metavar="<URL>")
    return parser.parse_args()

async def _db_calls(dbc: DatabaseConnection) -> None:
    async with dbc.engine.begin() as conn:
        await clean_db(conn)
        await setup_db(conn)
        await insert_example_data(conn)

async def insert_example_data(conn: AsyncConnection) -> None:
    result = await conn.execute(
        insert(User).values( # type: ignore[call-overload]
            email="example@example.com",
            username="example",
            first_name="Example",
            last_name="User",
            is_admin=True,
            password_hash=password_salt_hash_statement('password')
        ).returning(User.user_id)
    )
    print("#" * 30, f"Created user with id: {result.scalar_one()}", "#" * 30, sep="\n")

def main(args: argparse.Namespace) -> int:
    os.environ["ANIME_API_DATABASE_URL"] = args.database_url
    del DatabaseConnection._instance
    dbc = DatabaseConnection(args.database_url, echo=True)
    asyncio.run(_db_calls(dbc))
    return 0


if __name__ == "__main__":
    args = get_args()
    sys.exit(main(args))
