# Docker Dev 

A Docker template for a Python development environment.

## Features

- Multi-stage Docker build for optimized image size
- Poetry-based dependency management
- *optional* NVIDIA GPU support for machine learning workloads
- Persistent volumes for history, VS Code server, and HuggingFace cache, etc
- Gemini CLI support
- Makefile for simplified Docker operations

## Prerequisites

- Docker and Docker Compose
- Make (for using the Makefile commands)
- For GPU support: NVIDIA Container Toolkit

## Getting Started

### Basic Setup

1. Couple startup tips:

- You may need to create the volumes before running the containers:

```bash
docker volume create root-history
docker volume create vscode-server
docker volume create huggingface-cache
docker volume create google-vscode-extension-cache
```

- You also need a `.env` file to store your environment variables

```bash
touch .env
```

2. Clone this repository
3. Update the `pyproject.toml` with your project details and dependencies
4. Build the Docker image:

```bash
make build
```

5. Extract the lockfile from the container:

```bash
make extract-lock
```

You should now have a `poetry.lock` file in the `dev` directory.
