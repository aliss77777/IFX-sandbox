# 49ers FanAI Hub - Gradio Version

This is the Gradio version of the 49ers FanAI Hub, a conversational AI application that provides information about the San Francisco 49ers football team, players, games, and fan communities.

## Overview

This application uses:
- **Gradio** for the web interface
- **LangChain** for the agent framework
- **Neo4j** for the graph database
- **OpenAI** for the language model
- **Zep** for memory management

## Files

- `gradio_app.py` - Main application file with Gradio UI
- `gradio_utils.py` - Utility functions for the Gradio app
- `gradio_graph.py` - Neo4j graph connection without Streamlit dependencies
- `gradio_llm.py` - Language model initialization without Streamlit dependencies
- `gradio_requirements.txt` - Dependencies for the Gradio version

## Setup

1. Install the required dependencies:
   ```
   pip install -r gradio_requirements.txt
   ```

2. Set up environment variables (create a `.env` file or set them in your environment):
   ```
   # OpenAI API
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-4-turbo  # or another model

   # Neo4j Database
   NEO4J_URI=your_neo4j_uri
   NEO4J_USERNAME=your_neo4j_username
   NEO4J_PASSWORD=your_neo4j_password

   # Zep Memory (optional)
   ZEP_API_KEY=your_zep_api_key
   ```

3. Run the application:
   ```
   python gradio_app.py
   ```

4. Open your browser and navigate to the URL shown in the terminal (typically http://127.0.0.1:7860)

## Features

- Chat interface for asking questions about the 49ers
- Integration with Neo4j graph database for structured data queries
- Memory management with Zep for conversation history
- Support for various query types:
  - Information about players, games, and fans
  - Finding games based on descriptions
  - Discovering connections between people in the 49ers industry

## Differences from Streamlit Version

This Gradio version provides the same functionality as the Streamlit version but with a different UI framework. Key differences include:

1. **State Management**: Uses a custom AppState class instead of Streamlit's session_state
2. **UI Components**: Uses Gradio's chat interface instead of Streamlit's chat components
3. **Error Handling**: Uses console logging instead of Streamlit's error display
4. **Session Management**: Uses global variables for session IDs instead of Streamlit's session context

## Troubleshooting

- If you encounter connection issues with Neo4j, check your database credentials and network connectivity
- If the OpenAI API is not working, verify your API key and model name
- For Zep memory issues, ensure the Zep service is running and your API key is correct
