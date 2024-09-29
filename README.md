# Anime API

As a small side project wanted to make a way to track shows that I have watched, my progress with the show, and thoughts/reviews. Many other sites already exist like that but wanted to take a spin at it myself.

## Get Started

For the specific tools used and other information, the links to them are below.

```bash
# assuming uv installed
uv sync --frozen
source .venv/bin/activate
python3 src/anime_rest_api/main.py
```

## ToDos

- [ ] Add coverage reporting on GitHub Actions post testing.

## Code

Since this is meant to be a deployable application, the source is structured in a way to build a source/wheel distribution.

For more info on that see `pyproject.toml` for the **build-system** and other configuration options.

### Environment Variables

This project has configurable behavior by setting Environment variables for the process. All variables are prefixed by `ANIME_API_`. A shortlist includes:

- DATABASE_URL - how to connect to our SQL database.
- SECRET - encoding string for our JWTs

Environment variables will be loaded using `python-dotenv`. Run the following to place the file properly and then edit the values as necessary:

```bash
cp ./src/anime_rest_api/.env.template ./src/anime_rest_api/.env.production
```


## Database

Most of our code will be existing in an async runtime, we use [asyncpg](https://magicstack.github.io/asyncpg/current/index.html) as a Postgres Driver. Meaning the database is Postgres. In professional experience, this is the most versatile database for general purpose usage.

### Passwords and Cryptography

The password management is all executed with SQL queries using the enabled extension [pgcrypto](https://www.postgresql.org/docs/15/pgcrypto.html).

This allows us to stored salted and hashed passwords, and easily select or update them.

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE test_user (
    id SERIAL PRIMARY KEY,
    pw_hash text,
);

INSERT INTO test_user(pw_hash) VALUES(
    crypt(:pw, gen_salt('bf', 8))
);

SELECT
    pw_hash = crypt(:guess_password, pw_hash) AS pw_match
FROM test_user;
 pw_match
----------
 t
(1 row)
```

### Dependency and Virtual Environment Management

This project uses [UV](https://docs.astral.sh/uv/) to manage virtual environments and dependencies.

### Format and Linting

This project uses solely [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

### Static Analysis

As a proponent of typing Python code, this project uses [mypy](https://mypy-lang.org/) for static and type analysis. In professional experience, this has saved me many more times than I can count so will continue to use in my own personal projects.

### Pre Commit

All of the above are enforced using [pre-commit](https://pre-commit.com). To install the hooks, do the following:

```bash
source .venv/bin/activate
pre-commit install
```

## Tests

Tests are run using [pytest](https://docs.pytest.org/en/stable/) for unit testing and integration tests. To run all tests, do the following:

```bash
source .venv/bin/activate
pytest
```

Default options and other configuration are inside of [pyproject.toml](./pyproject.toml).

## Contributing

Open to all helpful contributions using PRs. Fork this repository, make changes on that copy and then open a PR to here.
