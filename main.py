import hashlib
import urllib

import asyncpg
import petname
from dotenv import dotenv_values
from fastapi import Depends, FastAPI, Header, HTTPException, status
from nanoid import generate

config = dotenv_values(".env")
app = FastAPI()

# !!! Note: this isn't meant to be secure
# could also use a cache ...


async def verify_token(x_key: str = Header(None)):
    if x_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    res = await conn.fetchrow(
        'select * from users where unique_key=$1',
        x_key
    )
    if res is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return dict(res)


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


# You have to pass a valid key
# curl -H "X-Key: your_key" http://127.0.0.1:8000/
@app.get("/")
async def get_root(user_info: dict = Depends(verify_token)):

    print("If you reach here, you're authorized")
    print(user_info)

    res = await conn.fetch(
        'select * from coordinates where user_id=1',
    )

    # asyncpg has a very nice conversion to a dict
    # combined with fastapi = ❤️
    entries = [dict(entry) for entry in res]
    return entries
