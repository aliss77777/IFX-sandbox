# 10. Security & Compliance

*   **Input Sanitization:** All user input from the chat interface will be sanitized on the backend to prevent injection attacks.
*   **API Keys:** Keys for the LLM service, Freeplay, Zep, and other external APIs must be stored securely as environment variables and not exposed on the client-side.
*   **WebSocket Security:** The WebSocket connection will use the secure `wss://` protocol in production.
*   **Authentication & Authorization:** For the MVP, there is no authentication. In the future, a standard JWT-based authentication mechanism could be implemented.
