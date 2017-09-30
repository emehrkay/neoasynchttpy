# neoasynchttpy

A simple async package for Neo4j HTTP.

## Installation

```
python setup.py install
```

## Usage

All requests are async and utilize the package [aiohttp](http://aiohttp.readthedocs.io/en/stable/index.html) so they must be executed within an ioloop.

```python
import asyncio
import random

from neoasynchttpy.connection import Connection


conn = Connection(url='localhost', username='neo4j', password='somepassword')

async def example():
    script = "CREATE (n {props}) RETURN n"
    params = {
        'props': {
            'name': 'mark'+ str(random.random())
        }
    }
    conn.statement(statement=script, parameters=params)
    resp = await conn.query()
    print(resp.results)


asyncio.get_event_loop().run_until_complete(example())
```
