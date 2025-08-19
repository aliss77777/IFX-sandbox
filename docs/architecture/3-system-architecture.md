# 3. System Architecture

The system follows a classic decoupled frontend-backend architecture.

*   **Frontend:** A Next.js application responsible for rendering the UI, managing user interactions, and communicating with the backend via WebSockets.
*   **Backend:** A FastAPI application that handles the core business logic, including WebSocket communication, vector search, and LLM integration.

```mermaid
graph TD
    A[User] -->|Interacts with| B(Frontend - Next.js);
    B -->|WebSocket| C(Backend - FastAPI);
    C -->|Vector Search| D(In-Memory Vector Store);
    C -->|LLM API Call| E(Large Language Model);
    C -->|Get Prompts| F(Freeplay);
    C -->|Get/Set Context| G(Zep);
```
