# 6. Epic 1: Foundation & Streaming Architecture

**Goal:** Establish the foundational monorepo structure, a working UI, and a **proven, end-to-end real-time streaming architecture**. This epic will deliver a functional, deployable application that demonstrates the core WebSocket communication pattern with dummy/hardcoded data, ensuring the riskiest technical component works before adding the AI logic.

## Story 1.1: Monorepo Structure & `ifx-app` Scaffolding
*As a developer, I want to formalize the monorepo structure and scaffold the new `ifx-app` frontend application, so that all project components are logically organized and ready for development.*
*   **Acceptance Criteria:**
    1.  The existing `app` directory is confirmed as the location for the Python/FastAPI backend.
    2.  A new `ifx-app` directory is created at the project root (`/workspace/ifx-app`).
    3.  A new Vite + React (TypeScript) application is scaffolded inside the `ifx-app` directory.
    4.  The root `README.md` is updated with a clear explanation of the monorepo structure (`app` for backend, `ifx-app` for frontend) and instructions on how to run each service.
    5.  The existing Docker setup is reviewed and confirmed to be sufficient for running the backend service.

## Story 1.2: Basic Frontend UI
*As a user, I want to see a basic chat interface with an input box and a message display area, so that I can begin to interact with the application.*
*   **Acceptance Criteria:**
    1.  The main application view renders a chat-style interface.
    2.  A text input field is present at the bottom of the screen.
    3.  A "Send" button is present next to the input field.
    4.  A display area for conversation history is present.
    5.  The UI uses basic `shadcn/ui` components for the inputs and buttons.
    6.  The UI is responsive and usable on both mobile and desktop screens.

## Story 1.3: Backend Health Check & WebSocket Endpoint
*As a developer, I want to add a health check and an initial WebSocket endpoint to the backend service, so that I can confirm the service is running and ready for real-time communication.*
*   **Acceptance Criteria:**
    1.  A `/health` endpoint is implemented and working.
    2.  A `/ws` endpoint is created in the FastAPI application that can accept WebSocket connections.

## Story 1.4: Streaming "Hello World"
*As a developer, I want to implement a "hello world" that streams a sample image and text over a WebSocket, so that I can prove the core real-time architecture is working end-to-end.*
*   **Acceptance Criteria:**
    1.  The `ifx-app` establishes a persistent WebSocket connection to the `/ws` endpoint.
    2.  When the user sends a message, the backend immediately sends a WebSocket message containing a hardcoded image URL (e.g., `{"type": "asset", ...}`).
    3.  The `ifx-app` displays the image.
    4.  The backend then sends a stream of hardcoded `text_chunk` messages.
    5.  The `ifx-app` renders these chunks as a "typing" text effect.
    6.  The backend sends a final `stream_end` message.

## Story 1.5: Continuous Deployment Setup
*As a developer, I want to set up continuous deployment for the application on Vercel, so that any changes pushed to the main branch are automatically deployed.*
*   **Acceptance Criteria:**
    1.  The monorepo is connected to a Vercel project.
    2.  Vercel is configured to correctly build and deploy the frontend application from the `ifx-app` directory.
    3.  Vercel is configured to correctly build and deploy the backend Docker container from the `app` directory.
    4.  A successful push to the `main` branch triggers a new deployment on Vercel.
    5.  The deployed application is accessible via a public Vercel URL.
