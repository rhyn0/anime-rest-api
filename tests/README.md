# Tests

Since the engine driver `asyncpg` is asynchronous, all of our tests make use of the `pytest-asyncio` runtime. There documentation is [here](https://pytest-asyncio.readthedocs.io/en/stable/).

## Some Gotchas

Since [`pytest`](https://docs.pytest.org/en/stable/) associates fixtures (setup/cleanup) as generator functions using this with async runtimes causes some fun behavior due to the garbage collection of the async generators being on the event loop. Meaning it happens eventually but maybe not **NOW**.

A great explanation on this behavior - and how to force some of the behavior is below:

[![mCoding Async Generator Video](http://img.youtube.com/vi/N56Jrqc7SBk/0.jpg)](https://youtu.be/N56Jrqc7SBk "Watch out for this (async) generator cleanup pitfall in Python")

As of writing there haven't been a lot of clean ways I've seen to handle this inside the `pytest.fixture` so have to add a few lines to actual tests to do *setup* and *cleanup*.

```python
async def test_thing(async_fixture_with_cleanup):
    async with contextlib.aclosing(async_fixture_with_cleanup) as gen:
        # run the setup
        yielded_value = await anext(gen)

        # omitted test code
        ...

        # resume the generator - causing cleanup
        with contextlib.suppress(StopAsyncIteration):
                await setup.asend(None)
    # fixture garbage collection point
```
