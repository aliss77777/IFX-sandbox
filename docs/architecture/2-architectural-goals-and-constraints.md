# 2. Architectural Goals and Constraints

## Goals

*   **Real-time Interaction:** The architecture must support low-latency, real-time communication between the frontend and backend.
*   **Modularity:** The system should be composed of loosely coupled components, allowing for easy replacement of the LLM, vector store, or other services.
*   **Scalability:** While the MVP is a demo, the architecture should be designed with future scalability in mind.
*   **Developer Experience:** The monorepo and decoupled services are intended to provide a smooth development experience.

## Constraints

*   **Frontend Technology:** The frontend stack is fixed: Next.js, React, TypeScript, and `shadcn/ui`.
*   **Backend Technology:** The backend stack is fixed: Python and FastAPI.
*   **MVP Focus:** The initial implementation will focus on the MVP scope outlined in the PRD, with an in-memory vector store.
