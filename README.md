# findmefindyou-server

This server requires [migrate](https://github.com/golang-migrate/migrate) to be installed on your computer to handle database migrations from the [migrations](./migrations) folder.

You need a `.env` file with the following content (change values as you wish):

```txt
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST="127.0.0.1"
POSTGRES_PORT=5432
```

## Running

For developing, I'm using a docker container for postgres with a named volume

```sh
$ docker volume create postgres-volume
$ docker run -d \
--name postgres-exercises \
-p 5432:5432 \
-e POSTGRES_PASSWORD=postgres \
-e PGDATA=/var/lib/postgresql/data/pgdata \
-v postgres-volume:/var/lib/postgresql/data \
postgres
```

Make sure postgres is running:

```sh
# Apply database migrations
$ make migrate
# Start the webserver in dev mode
$ uvicorn main:app --reload
```

## Makefile & Cleaning up

- If you wish to use a web interface, I've added adminer to the Makefile  
  `make adminer`.
- If you wish to use the `psql` cli, make sure it's installed and run `make pgcli`
- To delete everything from the db, use `make migrate-down`
