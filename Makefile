IMAGE_NAME = huge-ifx-api

extract-lock:
	@echo "Extracting poetry.lock from container..."
	@docker create --name temp-extract ${IMAGE_NAME}
	@docker cp temp-extract:/code/poetry.lock .
	@docker rm temp-extract
	@echo "Lock file updated locally."

build:
	docker compose -f docker-compose.yaml build

build-update:
	@echo "Deleting lock file..."
	rm -f poetry.lock
	@echo "Rebuilding image..."
	docker compose -f docker-compose.yaml build
	@$(MAKE) extract-lock

up:
	docker compose -f docker-compose.yaml up

command:
	docker exec -it ${IMAGE_NAME} /bin/bash

command-raw:
	docker compose run ${IMAGE_NAME} bash

clean-requirements:
	rm -f poetry.lock
	