import hashlib
import urllib

import asyncpg
import petname
from dotenv import dotenv_values
from fastapi import Depends, FastAPI, Header, HTTPException, UploadFile, File, status
from models.request_models import AccountReq, FriendCoordReq
from fastapi.staticfiles import StaticFiles
from nanoid import generate
import aiofiles

config = dotenv_values(".env")
app = FastAPI()

# Mount the image directory, you can download using
# wget http://<uvicorn_url>/img/<image_name>
app.mount("/img", StaticFiles(directory="img"))


async def verify_token(x_key: str = Header(None)):
    """ 
    Note: this isn't meant to be secure
    could also use a cache ...
    You have to pass a valid key
    curl -H "X-Key: your_key" http://127.0.0.1:8000/
    """
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
    """
    One connection is enough for this project as a global variable
    Pooling should be used instead (+ don't use a global variable)
    """
    global conn
    conn = await asyncpg.connect(user=config['POSTGRES_USER'], password=config['POSTGRES_PASSWORD'],
                                 host=config['POSTGRES_HOST'], port=config['POSTGRES_PORT'])


@app.on_event('shutdown')
async def shutdown():
    await conn.close()


@app.get("/init")
async def get_creds():
    """
    Display name maximum length is 18
    Unique key maximum length is 12
    """

    display_name = petname.Generate(3, separator='-', letters=5)
    unique_key = generate(size=12)

    return {
        'display_name': display_name,
        'unique_key': unique_key,
    }


@app.post("/create_account")
async def post_account(req: AccountReq):
    await conn.execute(
        """
        insert into users (display_name, unique_key, avatar_url)
        values
        ($1, $2, 'img/default_avatar.png');
        """,
        req.display_name, req.unique_key
    )
    return {"result": "ok"}

# TODO: add authorization to this, set the field in db for the user
# don't store the whole url in the db, just the path img/


@app.post("/upload_avatar")
async def post_avatar(photo: UploadFile = File(...), user_info: dict = Depends(verify_token)):
    location = f"img/{photo.filename}"
    async with aiofiles.open(location, 'wb') as out_avatar:
        content = await photo.read()
        await out_avatar.write(content)

    await conn.execute(
        """
        update users
        set avatar_url = $1
        where user_id = $2;
        """,
        location, user_info['user_id']
    )

    return {"avatar_url": location}


@app.get("/avatar_location")
async def get_avatar(user_info: dict = Depends(verify_token)):
    return {"avatar_url": user_info["avatar_url"]}

# TODO: This query gets all the coordinates for a friend


@app.post("/friend_coords")
async def get_friend_coords(req: FriendCoordReq, user_info: dict = Depends(verify_token)):
    res = await conn.fetch(
        """
        select coord.ts, coord.latitude, coord.longitude
            from users usr
            inner join coordinates coord
            on usr.user_id = coord.user_id
        where usr.user_id in
            (select f.friend_id
            from friends f
            where f.user_id = $1)
        and usr.display_name = $2;
        """,
        user_info['user_id'], req.friend_name
    )
    print(res)
    return [dict(entry) for entry in res]


@app.get("/friends")
async def get_friends(user_info: dict = Depends(verify_token)):
    res = await conn.fetch(
        """
        select usr.display_name, usr.avatar_url,
        (select ts 
            from coordinates coord 
            where coord.user_id = usr.user_id
            order by coord.coord_id desc
            limit 1
        )
            from users usr
        where usr.user_id in
            (select f.friend_id 
                from users u 
                inner join friends f 
                    on u.user_id = f.user_id 
            where u.user_id=$1);
        """,
        user_info['user_id']
    )

    return [dict(entry) for entry in res]


@app.get("/pending_friends")
async def get_friends(user_info: dict = Depends(verify_token)):
    res = await conn.fetch(
        """
        select usr.display_name, usr.avatar_url, pf.sent_at from pending_friends pf
            inner join users usr
            on pf.sender_id = usr.user_id
        where pf.receiver_id = $1;
        """,
        user_info['user_id']
    )

    return [dict(entry) for entry in res]


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
