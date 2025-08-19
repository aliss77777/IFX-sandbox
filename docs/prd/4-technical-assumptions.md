# 4. Technical Assumptions

## 4.1. Repository Structure

*   **Monorepo:** The project will use a monorepo to simplify development, dependency management, and deployment, especially with a small team. The frontend and backend code will live in separate, modular directories within this single repository to allow for a potential split in the future.

## 4.2. Service Architecture

*   **Decoupled Services:** The architecture will feature a decoupled frontend application and a backend API service, developed as modular components within the monorepo. This enforces a clean separation of concerns and allows for independent development and scaling of the services, even within a single repository.

## 4.3. Testing Requirements

*   **Unit + Integration:** The testing strategy will include both unit tests for individual components and integration tests to ensure the frontend and backend services communicate correctly.

## 4.4. Additional Technical Assumptions and Requests

*   **Language (Backend):** The backend will be built using Python and the FastAPI framework.
*   **Language (Frontend):** The frontend will be built using JavaScript/TypeScript with the React framework and Vite build tool.
*   **UI Components:** The `shadcn/ui` component library will be used for the frontend.
*   **Vector Store:** The MVP will use a simple, in-memory vector store (e.g., from LangChain or a similar library).
*   **Containerization:** The backend application must be containerized using Docker.
*   **Hosting (Frontend):** The frontend will be hosted on Vercel.
*   **Hosting (Backend):** The backend will be hosted on Vercel if feasible, otherwise on a suitable container-hosting platform.
*   **LLM:** A high-performance LLM from a major provider (e.g., Google, OpenAI, Anthropic) will be used. The specific model will be chosen based on performance and cost analysis.
