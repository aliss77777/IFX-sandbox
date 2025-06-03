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

# Build the Docker image for the 'runtime' stage in api/Dockerfile, tagged as huge-ifx-api:prod
build-prod:
	cd api && docker build --platform linux/amd64 -f Dockerfile --target runtime -t huge-ifx-api:prod .

# Build the prod image and run it locally, mapping ports 7860 and 8000
up-build-prod: build-prod
	docker run --rm -it -p 7860:7860 -p 8000:8000 --env-file .env -e DEV_MODE=true huge-ifx-api:prod

# Push the prod image to GitHub Container Registry
push-prod-ghcr:
	docker tag huge-ifx-api:prod ghcr.io/ylassohugeinc/ifx-huge-league-api:prod
	docker push ghcr.io/ylassohugeinc/ifx-huge-league-api:prod
