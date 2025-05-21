# Huge IFX API

An AI-powered sports fan assistant that creates natural language, multimodal, and personalized experiences around professional sports teams, players, games, rules, and fan communities. The app delivers conversational responses enhanced with visuals and session memory.

**Fictional League:** Huge League  
- International soccer league, 23-player squads, 4-3-3 base formation.
- Teams:
    - Yucatán Force (Mérida, Mexico): Mayan pride, fortress stadium "El Templo del Sol".
    - Tierra Alta FC (San José, Costa Rica): Highlanders, eco-friendly, smart play.
    - Everglade FC (Miami, USA): Flashy, wild, South Florida flair.
    - Fraser Valley United (Abbotsford, Canada): Vineyard roots, top youth academy.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Setup](#setup)
- [Deployment](#deployment)
- [API Usage](#api-usage)
- [Prompt Management (Freeplay)](#prompt-management-freeplay)
- [Memory (Zep)](#memory-zep)
- [Agents (LangGraph)](#agents-langgraph)
- [LLM (OpenAI)](#llm-openai)
- [Development & Contributing](#development--contributing)
- [License](#license)

---

## Features

- Conversational AI assistant for Huge League soccer fans
- Multimodal responses (text, visuals)
- Personalized session memory
- Prompt management and logging
- Modular agent-based workflow

---

## Architecture

```mermaid
flowchart TD
    UI[Gradio UI (HuggingFace Spaces)]
    API[FastAPI (server.py)]
    Workflow[LangGraph Agent Workflow]
    Freeplay[Prompt Management (Freeplay)]
    Zep[Memory (Zep)]
    OpenAI[LLM (OpenAI)]
    Tools[Custom Tools]
    UI --> Workflow
    Workflow --> Freeplay
    Workflow --> Zep
    Workflow --> OpenAI
    Workflow --> Tools
```

- **UI:** Gradio-based, runs via `server_gradio.py`
- **Workflow:** Orchestrated by LangGraph (`workflows/base.py`)
- **Prompt Management:** Freeplay (`utils/freeplay_helpers.py`)
- **Memory:** Zep (`utils/zep_helpers.py`)
- **LLM:** OpenAI (gpt-4o-mini)
- **Tools:** Player/Game search (`tools/`)

---

## Tech Stack

- [Gradio](https://gradio.app/) (HuggingFace Spaces)
- [FastAPI](https://fastapi.tiangolo.com/) (not used b/c we went with gradio)
- [Freeplay](https://freeplay.ai/) (Prompt management)
- [Zep](https://getzep.com/) (Session memory)
- [LangGraph](https://langchain-ai.github.io/langgraph/) (Agent workflow)
- [OpenAI](https://openai.com/) (LLM)
- [Docker](https://www.docker.com/), [Poetry](https://python-poetry.org/) for dependency management

---

## Setup

**Prerequisites:**  
- [Docker](https://www.docker.com/) installed

**Quickstart:**

```bash
make build
make up
```

- The app will be available at [http://localhost:8000/](http://localhost:8000/)

**Environment Variables:**
- See `.env.example` (TODO: Document required env vars for Freeplay, Zep, OpenAI, etc.)
- Ask Liss for env vars.

---

## Deployment

### HuggingFace Spaces

App is hosted at: [https://huggingface.co/spaces/ryanbalch/IFX-huge-league](https://huggingface.co/spaces/ryanbalch/IFX-huge-league)

To deploy:

1. **Clone this repo** under your HuggingFace repo (in the `IFX-huge-league` folder). You will need it for deploys, etc.
2. **Deployment Targets:**
    - GitHub: [aliss77777/IFX-sandbox](https://github.com/aliss77777/IFX-sandbox/tree/huge-league)
    - HuggingFace: [ryanbalch/IFX-huge-league](https://huggingface.co/spaces/ryanbalch/IFX-huge-league/tree/main)
    - Docker images: `ghcr.io/rbalch/huge-ifx-api:prod`

3. **Deployment Steps:**

    ```bash
    # build the final image
    make build-prod
    # push to GitHub Container Registry
    make push-prod-ghcr
    # trigger a build in the HuggingFace repo
    cd IFX-huge-league && make trigger-build
    ```

    Then wait for the build to finish: [HuggingFace container logs](https://huggingface.co/spaces/ryanbalch/IFX-huge-league?logs=container)

---

## API Usage

- **Gradio UI:** Main entrypoint is `server_gradio.py`.  
  Launches the conversational interface for Huge League fans.
- **FastAPI:** `server.py` provides a minimal API (mostly for development/debug).

### Endpoints

| Path   | Method | Description         |
|--------|--------|---------------------|
| `/`    | GET    | Healthcheck/home    |

(TODO: Document additional endpoints if present)

---

## Prompt Management (Freeplay)

- Integrated via `utils/freeplay_helpers.py`
- Prompts are fetched, formatted, and logged using Freeplay.
- See `scripts/freeplay_playground.py` for usage examples.

---

## Memory (Zep)

- Integrated via `utils/zep_helpers.py`
- Session/user memory managed via Zep.
- See `scripts/zep_playground.py` for usage examples.

---

## Agents (LangGraph)

- Workflow orchestrated in `workflows/base.py` using LangGraph.
- Integrates LLM, memory, prompt management, and tools.

---

## LLM (OpenAI)

- Uses OpenAI models (e.g., `gpt-4o-mini`) via LangChain/LangGraph.
- API keys required. (TODO: Document setup)

---

## Development & Contributing

- All development is Dockerized.  
- Use Poetry for dependency management (`poetry add <pkg>` inside the container).
- Follow PEP8, prefer two blank lines between unrelated classes/functions.
- See `Makefile` for available commands.

---

## Makefile Commands

The following `make` commands are available for development, build, and deployment workflows:

| Command               | Description |
|-----------------------|-------------|
| `make build`          | Build all Docker images using `docker-compose.yaml`. |
| `make build-update`   | Remove `poetry.lock`, rebuild Docker image, and extract new lock file from the container. **Note:** This is not needed for local development. Only use if you're trying to update dependencies. |
| `make up`             | Start all services using Docker Compose. |
| `make command`        | Open an interactive shell inside the running `huge-ifx-api` container. |
| `make command-raw`    | Run a bash shell in a new container using Docker Compose (not the running one). |
| `make clean-requirements` | Remove the local `poetry.lock` file. |
| `make extract-lock`   | Extract the `poetry.lock` file from a built container to your local directory. **Note:** This is only needed if you've been deleting the lock file because build will not have access to local lock file. |
| `make build-prod`     | Build the Docker image for the `runtime` stage in `api/Dockerfile`, tagged as `huge-ifx-api:prod`. Used for production deploys. |
| `make up-build-prod`  | Build and run the production image locally, mapping ports 7860 and 8000, with `.env` and `DEV_MODE=true`. |
| `make push-prod-ghcr` | Tag and push the production image to GitHub Container Registry at `ghcr.io/rbalch/huge-ifx-api:prod`. |

**Typical workflow:**
- Use `make build` and `make up` for local development.
- Use `make build-prod`, `make push-prod-ghcr`, and `make trigger-build` (in the HuggingFace repo) for production deployment.

---

## License

(TODO: Add license info)
