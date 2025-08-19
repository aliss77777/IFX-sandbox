# 7. Communication Protocol

Communication between the frontend and backend will be exclusively over WebSockets. The following message types are defined:

*   **Client to Server:**
    *   `user_query`: A JSON message containing the user's text query.

*   **Server to Client:**
    *   `asset`: A JSON message containing the URL or data of the visual asset found by the vector search.
    *   `text_chunk`: A JSON message containing a chunk of the streamed text response from the LLM.
    *   `stream_end`: A JSON message indicating the end of the text stream.
    *   `status`: A JSON message to provide real-time feedback on the system's status (e.g., "Searching for players...").
