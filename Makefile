PROJECT_NAME := $(notdir $(CURDIR))
IMAGE_NAME := ${PROJECT_NAME}-dev

extract-lock:
	@echo "Extracting poetry.lock from container..."
	@docker create --name temp-extract ${IMAGE_NAME}
	@docker cp temp-extract:/home/dev/poetry.lock ./dev/poetry.lock
	@docker rm temp-extract
	@echo "Lock file updated locally."

build:
	docker compose -f docker-compose.yaml build

build-update:
	@echo "Deleting lock file..."
	rm -f dev/poetry.lock
	@echo "Rebuilding image..."
	docker compose -f docker-compose.yaml build
	@$(MAKE) extract-lock

build-gpu:
	docker compose -f docker-compose.yaml -f docker-compose-nvidia.yaml build

build-release:
	cd api && docker build --platform linux/amd64 -f Dockerfile --target release -t ${IMAGE_NAME}:release .

up:
	docker compose -f docker-compose.yaml up

up-gpu:
	docker compose -f docker-compose.yaml -f docker-compose-nvidia.yaml up

run-backend:
	docker compose exec dev uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

command:
	docker exec -it ${IMAGE_NAME}-1 zsh

command-raw:
	docker compose run dev zsh

command-ifx-app:
	docker exec -it ${PROJECT_NAME}-ifx-app-1 sh

command-raw-gpu:
	docker compose -f docker-compose.yaml -f docker-compose-nvidia.yaml run ${IMAGE_NAME} bash

clean-requirements:
	rm -f dev/poetry.lock
	
prune-containers:
	docker container prune -f

verify-proxy:
	curl -sS -o /dev/null -w "%{{http_code}}\n" http://0.0.0.0:3000
