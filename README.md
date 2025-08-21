# Huge IFX Soccer AI Demo

This repository contains the source code for the Huge IFX Soccer AI Demo, a real-time, conversational AI application that allows users to interact with a fictional soccer league.

## Monorepo Structure

The project is organized as a monorepo with the following structure:

-   `/app`: The backend Python application, built with FastAPI.
-   `/ifx-app`: The frontend Next.js application.
-   `/docs`: Project documentation, including PRD and architecture.
-   `/data`: Data for the fictional Huge League.
-   `/tests`: Application tests.

## Getting Started

### Prerequisites

-   Docker and Docker Compose
-   Make (for using the Makefile commands)

### Running the Application

1.  **Create Volumes and Environment File:**

    ```bash
    docker volume create root-history
    docker volume create vscode-server
    docker volume create huggingface-cache
    docker volume create google-vscode-extension-cache
    touch .env
    ```

2.  **Build and Start the Development Environment:**

    ```bash
    make build
    make up
    ```

    This will start the development environment, which consists of two services:
    -   `dev`: The main development container. It contains the Python backend and proxies requests to the frontend.
    -   `ifx-app`: The frontend Next.js application container.

3.  **Run the Backend Service:**

    The backend FastAPI server does not start automatically. To run it, open a new terminal and execute the following command:

    ```bash
    make run-backend
    ```

    This will start the backend server with hot-reloading at `http://localhost:8000`.

4.  **Access the Application:**

    -   The frontend application will be available at [http://localhost:3000](http://localhost:3000).
    -   The backend API will be available at [http://localhost:8000](http://localhost:8000).

## Development

### Working with the Development Container

The `dev` container is your main development environment. It's a full-featured environment that comes with all the tools you need for this project, including:

-   The Python backend application.
-   `gemini-cli` for interacting with the Gemini API.
-   A proxy to the frontend `ifx-app` container.
-   All the necessary dependencies to run, test, and debug the application.

To open a shell inside the `dev` container, use the following command:

```bash
make command
```

From within the `dev` container, you can run the backend, run tests, and use the `gemini-cli`.

### Makefile Commands

The `Makefile` contains several useful commands for development:

-   `make build`: Build the docker containers.
-   `make up`: Start the docker containers.
-   `make run-backend`: Start the backend FastAPI server with hot-reloading.
-   `make command`: Open a shell inside the `dev` container.
-   `make command-ifx-app`: Open a shell inside the `ifx-app` container.
-   `make build-gpu`: Build the docker containers with GPU support.
-   `make up-gpu`: Start the docker containers with GPU support.
-   `make clean-requirements`: Remove the local `poetry.lock` file.
-   `make prune-containers`: Remove stopped containers.
-   `make verify-proxy`: Verify that the proxy is running.