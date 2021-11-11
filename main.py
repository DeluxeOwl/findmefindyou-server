import hashlib
import urllib

import asyncpg
import petname
from dotenv import dotenv_values
from fastapi import FastAPI
from nanoid import generate

config = dotenv_values(".env")
app = FastAPI()


@app.on_event('startup')
async def startup():
    # One connection is enough for this project as a global variable
    # Pooling should be used instead (+ don't use a global variable)
    global conn
    conn = await asyncpg.connect(user=config['POSTGRES_USER'], password=config['POSTGRES_PASSWORD'],
                                 host=config['POSTGRES_HOST'], port=config['POSTGRES_PORT'])


@app.on_event('shutdown')
async def shutdown():
    await conn.close()


@app.get("/init")
async def get_creds():
    # maximum length is 18 for the name
    display_name = petname.Generate(3, separator='-', letters=5)
    unique_key = generate(size=12)

    return {
        'display_name': display_name,
        'unique_key': unique_key,
    }


@app.get("/")
async def get_root():
    res = await conn.fetch(
        'select * from coordinates where user_id=1',
    )

    # asyncpg has a very nice conversion to a dict
    # combined with fastapi = ❤️
    entries = [dict(entry) for entry in res]
    return entries
