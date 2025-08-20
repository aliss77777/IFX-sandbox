# Huge IFX Soccer AI Demo

This repository contains the source code for the Huge IFX Soccer AI Demo, a real-time, conversational AI application that allows users to interact with a fictional soccer league.

## Monorepo Structure

The project is organized as a monorepo with the following structure:

-   **/app**: The backend Python application, built with FastAPI.
-   **/ifx-app**: The frontend Next.js application.
-   **/docs**: Project documentation, including PRD and architecture.
-   **/data**: Data for the fictional Huge League.
-   **/tests**: Application tests.

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

2.  **Build and Run the Services:**
    ```bash
    docker-compose up --build
    ```

    This will start both the backend and frontend services.

    -   The frontend application will be available at [http://localhost:3000](http://localhost:3000).
    -   The backend service runs in the `dev` container.

3.  **Run the Backend Service:**

    To run the backend FastAPI server, use the following make command:

    ```bash
    make run-backend
    ```

    This will start the backend server with hot-reloading, so any changes you make to the backend code will be automatically applied.
