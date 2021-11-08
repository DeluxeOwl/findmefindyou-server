import asyncpg
from dotenv import dotenv_values
from fastapi import FastAPI

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


@app.get("/")
async def get_root():
    res = await conn.fetch(
        'select * from test'
    )

    # asyncpg has a very nice conversion to a dict
    # combined with fastapi = ❤️
    entries = [dict(entry) for entry in res]
    return entries
