# 6. Data Management

*   **Content:** The fictional player and team data is stored as JSON files in the `data/huge-league/players` directory.
*   **Vector Store:** For the MVP, an in-memory vector store (e.g., FAISS) will be used. This store will be populated with embeddings of the player and team data at application startup.
*   **Session Data:** Session-specific data, such as conversation history and user preferences (e.g., favorite team), will be managed by Zep.
