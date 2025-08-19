# 4. Frontend Architecture

The frontend is a Next.js application using the App Router.

*   **Framework:** Next.js
*   **Language:** TypeScript
*   **UI Components:** `shadcn/ui`
*   **State Management:** React hooks and context for local state. For a larger application, a more robust state management library like Zustand or Redux could be considered.
*   **Communication:** A dedicated WebSocket client will be implemented to handle the real-time communication with the backend. This client will be responsible for sending user queries and receiving and processing the stream of responses (assets, text chunks, status updates).
*   **Component Structure:** The UI is broken down into reusable components as described in the `front-end-spec.md`: `AssetDisplay`, `ChatHistory`, `ChatInput`, and `DevPanel`.
