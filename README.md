---
title: ifx-sandbox
app_file: gradio_app.py
sdk: gradio
sdk_version: 5.24.0
---
# 49ers FanAI Hub - Gradio Version

This is a Gradio-based chatbot application that provides information about the San Francisco 49ers, players, games, and fans. The application uses LangChain, Neo4j, and Zep for memory management.

## Features

- Chat interface for asking questions about the 49ers
- Integration with Neo4j graph database for structured data queries
- Vector search for finding game summaries
- Memory management with Zep for conversation history
- Game Recap component that displays visual information for game-related queries

## Prerequisites

- Python 3.9+
- Neo4j database (local or Aura)
- OpenAI API key
- Zep API key

## Installation

1. Clone the repository
2. Install the required packages:

```bash
pip install -r gradio_requirements.txt
```

3. Set up your environment variables:
   - Copy `.env.example` to `.env` in the root directory
   - Fill in your API keys and credentials

Example `.env` file:
```
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o
AURA_CONNECTION_URI=your_neo4j_uri
AURA_USERNAME=your_neo4j_username
AURA_PASSWORD=your_neo4j_password
ZEP_API_KEY=your_zep_api_key
```

> **IMPORTANT**: Never commit your actual API keys or credentials to the repository. The `.env` files are included in `.gitignore` to prevent accidental exposure of sensitive information.

## Running the Application

To run the Gradio application:

```bash
python gradio_app.py
```

This will start the Gradio server and open the application in your default web browser.

## Project Structure

- `gradio_app.py`: Main Gradio application
- `gradio_agent.py`: Agent implementation using LangChain for Gradio
- `gradio_graph.py`: Neo4j graph connection for Gradio
- `gradio_llm.py`: Language model configuration for Gradio
- `gradio_utils.py`: Utility functions for Gradio
- `prompts.py`: System prompts for the agent
- `tools/`: Specialized tools for the agent
  - `cypher.py`: Tool for Cypher queries to Neo4j
  - `vector.py`: Tool for vector search of game summaries
  - `game_recap.py`: Tool for game recaps with visual component
- `components/`: UI components
  - `game_recap_component.py`: Game recap visual component
- `data/`: Data files and scripts
  - Various scripts and CSV files with 49ers data
- `docs/`: Documentation
  - `requirements.md`: Detailed product and technical requirements
  - `game_recap_implementation_instructions.md`: Implementation details for the game recap feature

## Game Recap Component

The Game Recap feature provides visual information about games in addition to text-based summaries. When a user asks about a specific game, the application:

1. Identifies the game being referenced
2. Retrieves game data from the Neo4j database
3. Displays a visual component with team logos, scores, and other game information
4. Generates a text summary in the chat

Note: As mentioned in `docs/game_recap_implementation_instructions.md`, this component is still a work in progress. Currently, it displays above the chat window rather than embedded within chat messages.

## Security Considerations

This repository includes:
- `.gitignore` file to prevent committing sensitive information
- `.env.example` files showing required environment variables without actual values
- No hardcoded API keys or credentials in the code

Before pushing to a public repository:
1. Ensure all sensitive information is in `.env` files (which are ignored by git)
2. Verify no API keys or credentials are hardcoded in any files
3. Check that large data files or binary files are properly ignored if needed

## Usage

1. Start the application
2. Ask questions about the 49ers, such as:
   - "Who are the current players on the 49ers roster?"
   - "Tell me about the 49ers game against the Chiefs"
   - "Which fan communities have the most members?"
   - "Show me the recap of the 49ers vs. Vikings game"

The application will use the appropriate tools to answer your questions based on the data in the Neo4j database.
