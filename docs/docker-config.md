# Docker Dev Configuration

This document explains how the development containers are configured, why `fixuid` is used, how volumes are mounted, and how to build/run the services locally.

- Services: `dev` (Python/Poetry), `ifx-app` (Next.js)
- UID/GID alignment: `fixuid` ensures files created in containers map to your host user
- Volume strategy: bind mounts for source, anonymous volumes for build caches with a controlled chown step

## Directory layout
- Dev image: `dev/Dockerfile`
- Web app image: `ifx-app/Dockerfile`
- Web app entrypoint: `ifx-app/docker-entrypoint.sh`
- Compose: `docker-compose.yaml`

## Why fixuid
When you bind-mount the repo, container users must match your host UID/GID or you’ll see permission issues. `fixuid` remaps the container user to your host’s UID/GID at runtime.

- `dev` uses `fixuid` with user `dev:dev` and `ENTRYPOINT ["fixuid","-q","--"]`.
- `ifx-app` uses `fixuid` with user `node:node`, but additionally performs a chown on anonymous volumes used for build artifacts.

Notes:
- `fixuid` remaps existing files owned by the configured UID/GID inside the container. It does not automatically change ownership of Docker-created anonymous volumes, which default to `root:root`.
- Therefore, a small chown step is still required for `ifx-app`'s anonymous volumes.

## Service: dev (Python/Poetry)
Path: `dev/Dockerfile`

Key points:
- Based on `python:3.13-slim`.
- Installs `fixuid` and configures it for `dev:dev`.
- Creates a shared virtualenv at `/opt/venv` and installs Poetry globally.
- Sets up Zsh + Oh My Zsh and misc CLI tooling.
- Default entrypoint runs `fixuid` and drops into `zsh`.

Compose mounts for `dev` (excerpt from `docker-compose.yaml`):
- `./:/workspace` (bind mount repo)
- Developer caches/volumes:
  - `root-history:/home/dev/history`
  - `vscode-server:/home/dev/.vscode-server`
  - `huggingface-cache:/home/dev/.cache/huggingface`
  - `google-vscode-extension-cache:/home/dev/.cache/google-vscode-extension`

## Service: ifx-app (Next.js)
Path: `ifx-app/Dockerfile`

Key points:
- Based on `node:18-alpine`.
- Installs `fixuid` and configures it for `node:node`.
- Uses an entrypoint script `ifx-app/docker-entrypoint.sh`.
- The entrypoint:
  1) Runs as root to ensure the build-cache mounts exist and are writable: `mkdir -p /app/.next /app/node_modules` and `chown -R node:node` on those paths.
  2) Re-execs itself via `fixuid -q --` to drop privileges to `node` remapped to host UID/GID.
  3) Starts the Next.js dev server with the correct package manager (detects yarn/npm/pnpm by lockfile).

Compose mounts for `ifx-app`:
- `./ifx-app:/app` (bind mount source)
- `/app/node_modules` (anonymous volume)
- `/app/.next` (anonymous volume)

Rationale:
- Keeping `node_modules` and `.next` as anonymous volumes avoids polluting the host repo with build artifacts.
- The entrypoint takes care of ownership so the `node` user can write to those mounts.

## Build and run

### One-time setup (dev service volumes)
Create developer volumes referenced by `dev`:
```bash
docker volume create vscode-server
docker volume create huggingface-cache
docker volume create google-vscode-extension-cache
```
Create an `.env` file (if needed):
```bash
touch .env
```

### Build images
```bash
# Build both services
docker compose build

# Or build individually
docker compose build dev
docker compose build ifx-app
```

### Run services
```bash
# Bring up both
docker compose up

# Or just the web app
docker compose up ifx-app

# Stop
docker compose down
```

Ports:
- `ifx-app`: http://localhost:3000
- `dev`: interactive shell only (default command `sleep infinity`) unless you override.

## Common issues & troubleshooting
- Permission denied writing to `.next` or `node_modules`:
  - Ensure you’re using the updated `ifx-app` image with `fixuid` and the entrypoint script.
  - Rebuild the image after Dockerfile changes: `docker compose build ifx-app`.
  - Confirm the compose service does not override the command (so the entrypoint can run).

- Container exits with code 137:
  - This often means it was stopped (SIGKILL/Out-of-memory). Check `docker logs <container>` for context.

- Bind-mount alternative:
  - If you prefer to keep build artifacts on host (and skip chown), bind-mount them instead:
    ```yaml
    volumes:
      - ./ifx-app:/app
      - ./ifx-app/node_modules:/app/node_modules
      - ./ifx-app/.next:/app/.next
    ```
  - Add `ifx-app/node_modules` and `ifx-app/.next` to `.gitignore`.

## File references
- `dev/Dockerfile`: fixuid setup for `dev` user.
- `ifx-app/Dockerfile`: fixuid setup for `node` user and entrypoint wiring.
- `ifx-app/docker-entrypoint.sh`: chown mounts → `fixuid` → start Next.js.
- `docker-compose.yaml`: volumes and ports for both services.

## Make targets (Python dev)
The repo uses Poetry inside the `dev` container. Typical flow:
- Build the dev image: `make build`
- Extract lockfile (if you use that workflow): `make extract-lock`

Follow project-specific Makefile targets to run tests or app commands; ensure all Python dependency installs use `poetry add` inside the `dev` container.
