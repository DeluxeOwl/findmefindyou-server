import hashlib
import urllib
from datetime import datetime, timedelta

import aiofiles
import asyncpg
import petname
from dotenv import dotenv_values
from fastapi import (Depends, FastAPI, File, Header, HTTPException, UploadFile,
                     status)
from fastapi.staticfiles import StaticFiles
from nanoid import generate

from models.request_models import (AccountReq, FriendCoordReq, FriendAddDeleteReq,
                                   UploadCoordReq, AcceptDeclineFriendReq)

from typing import List

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


# TODO: yeah, I got some weird error once about not being able to execute multiple operations
# should use a pool
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


@app.post("/friend_coords")
async def get_friend_coords(req: FriendCoordReq, user_info: dict = Depends(verify_token)):

    start_date = None
    end_date = None

    query_string = """
    select distinct(coord.ts), coord.latitude, coord.longitude
        from users usr
        inner join coordinates coord
        on usr.user_id = coord.user_id
    where usr.user_id in
        (select f.friend_id
        from friends f
        where f.user_id = $1)
    and usr.display_name = $2
    """

    # check if parameters are provided
    # try to parse the dates
    # check if start_time is greater than one week ago
    # return nothing if so

    if req.start_date:
        try:
            start_date = datetime.strptime(
                req.start_date, '%Y-%m-%d %H:%M:%S.%f')
            if datetime.now() - start_date > timedelta(days=7):
                return []
        except ValueError:
            print("error when parsing start_date")
            return []

    if req.end_date:
        try:
            end_date = datetime.strptime(
                req.end_date, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            print("error when parsing end_date")
            return []

    if start_date and end_date is None:
        res = await conn.fetch(
            query_string +
            "and coord.ts >= $3 order by ts",
            user_info['user_id'], req.friend_name, start_date
        )
        return [dict(entry) for entry in res]

    if start_date and end_date:
        res = await conn.fetch(
            query_string +
            'and coord.ts >= $3 and coord.ts <= $4 order by ts',
            user_info['user_id'], req.friend_name, start_date, end_date
        )
        return [dict(entry) for entry in res]

    # get maximum from the last 7 days
    res = await conn.fetch(
        query_string +
        "and coord.ts > NOW() - INTERVAL '7 days' order by ts",
        user_info['user_id'], req.friend_name
    )
    res_dict = [dict(entry) for entry in res]
    for entry in res_dict:
        entry['ts'] = ' '.join(str(entry['ts']).split('T'))[:-3]
    return res_dict


@app.delete("/delete_friend")
async def delete_friend(req: FriendAddDeleteReq, user_info: dict = Depends(verify_token)):
    # this is bad practice, you should do it in a transaction
    async with conn.transaction():
        friend_id = await conn.fetchval(
            """
            select f.friend_id from friends f
                inner join users usr
                on f.friend_id = usr.user_id
                where f.user_id = $1
            and usr.display_name = $2
            """,
            user_info['user_id'], req.friend_name
        )

        if friend_id is None:
            return {"result": "error"}

        await conn.execute(
            """
            delete from friends
            where user_id = $1 and friend_id = $2
            or user_id = $2 and friend_id = $1
            """,
            user_info['user_id'], friend_id
        )

        return {"result": "ok"}


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
async def get_pending_friends(user_info: dict = Depends(verify_token)):
    res = await conn.fetch(
        """
        select usr.display_name, usr.avatar_url, pf.sent_at from pending_friends pf
            inner join users usr
            on pf.sender_id = usr.user_id
        where pf.receiver_id = $1;
        """,
        user_info['user_id']
    )
    res_dict = [dict(entry) for entry in res]

    for entry in res_dict:
        entry['sent_at'] = ' '.join(str(entry['sent_at']).split('T'))[:-3]
    return res_dict


@app.get("/pending_friends_number")
async def get_pending_friends_number(user_info: dict = Depends(verify_token)):
    notif_nr = await conn.fetchval(
        """
        select count(*) from pending_friends pf
            inner join users usr
            on pf.sender_id = usr.user_id
        where pf.receiver_id = $1;
        """,
        user_info['user_id']
    )

    return {"result": notif_nr}


@app.post("/friend_req")
async def friend_req(req: AcceptDeclineFriendReq, user_info: dict = Depends(verify_token)):

    if req.action != 'accept' and req.action != 'decline':
        print("got here")
        return {"result": "error"}

    sender_id = await conn.fetchval(
        """
        select p.sender_id from pending_friends p
            inner join users u
            on u.user_id = p.sender_id
        where p.receiver_id = $1 and u.display_name = $2
        """,
        user_info['user_id'], req.friend_name
    )

    if sender_id is None:
        return {"result": "error"}
    async with conn.transaction():
        if req.action == 'accept':
            await conn.execute(
                """
                delete from pending_friends
                where receiver_id = $1 and sender_id = $2
                """,
                user_info['user_id'], sender_id
            )
            await conn.execute(
                """
                insert into friends (user_id, friend_id)
                values
                ($1, $2),
                ($2, $1);
                """,
                user_info['user_id'], sender_id
            )
        if req.action == 'decline':
            await conn.execute(
                """
                delete from pending_friends
                where receiver_id = $1 and sender_id = $2
                """,
                user_info['user_id'], sender_id
            )

    return {"result": "ok"}


@app.post("/send_friend_req")
async def send_friend_req(req: FriendAddDeleteReq, user_info: dict = Depends(verify_token)):
    receiver_id = await conn.fetchval(
        """
        select user_id 
        from users
        where display_name = $1
        """,
        req.friend_name
    )
    if receiver_id is None:
        return {"result": "error"}
    await conn.execute(
        """
        insert into pending_friends (receiver_id, sender_id, sent_at)
        values ($1, $2, $3)
        """,
        receiver_id, user_info['user_id'], datetime.now()
    )

    return {"result": "ok"}


@app.post("/upload_coords")
async def upload_coords(req: List[UploadCoordReq], user_info: dict = Depends(verify_token)):
    if not req:
        return {"result": "empty request"}
    # transaction doesnt seem to work but oh well
    for entry in req:
        async with conn.transaction():
            try:
                await conn.execute(
                    """
                insert into coordinates (user_id, ts, latitude, longitude)
                values
                ($1, $2, $3, $4);
                """,
                    user_info['user_id'], datetime.strptime(
                        entry.timestamp, '%Y-%m-%d %H:%M:%S.%f'), entry.latitude, entry.longitude
                )
            except Exception:
                return {"result": "error"}
    # get latest ts and return it
    latest_ts = await conn.fetchval(
        """
        select ts from coordinates 
            where user_id = $1 
        order by coord_id desc 
        limit 1;
        """,
        user_info['user_id']
    )
    # date 'parsing' lmao ⟶ gives the date like this 2022-01-07 14:00:00.685
    latest_ts = ' '.join(str(latest_ts).split('T'))[:-3]
    return {"result": latest_ts}


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
