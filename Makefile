.PHONY: migrate pgcli adminer test-insert

ifneq (,$(wildcard ./.env))
    include .env
    export
endif

pgcli:
	psql --username=$(POSTGRES_USER) --host=$(POSTGRES_HOST) \
	--port=$(POSTGRES_PORT)

test-insert:
	psql --username=$(POSTGRES_USER) --host=$(POSTGRES_HOST) \
	--port=$(POSTGRES_PORT) --file test_values.sql

adminer:
	docker run --rm -ti --network host adminer

migrate:
	migrate -source file://migrations \
	 		-database postgres://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/postgres?sslmode=disable up

migrate-down:
	migrate -source file://migrations \
	 		-database postgres://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/postgres?sslmode=disable down