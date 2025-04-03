# 49ers FanAI Hub - Streamlit Version

This is a Streamlit-based chatbot application that provides information about the San Francisco 49ers, players, games, and fans. The application uses LangChain, Neo4j, and Zep for memory management.

## Features

- Chat interface for asking questions about the 49ers
- Integration with Neo4j graph database for structured data queries
- Vector search for finding game summaries
- Memory management with Zep for conversation history

## Prerequisites

- Python 3.9+
- Neo4j database (local or Aura)
- OpenAI API key
- Zep API key

## Installation

1. Clone the repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
   - Copy `.env.example` to `.env` in the root directory
   - Copy `data/.env.example` to `data/.env` in the data directory
   - Fill in your API keys and credentials in both `.env` files

Example `.env` file:
```
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o
AURA_CONNECTION_URI=your_neo4j_uri
AURA_USERNAME=your_neo4j_username
AURA_PASSWORD=your_neo4j_password
ZEP_API_KEY=your_zep_api_key
```

Alternatively, you can set up your credentials in the `.streamlit/secrets.toml` file:

```toml
# OpenAI API credentials
OPENAI_API_KEY = "your_openai_api_key"
OPENAI_MODEL = "gpt-4o"  # Or your preferred model

# Neo4j credentials
NEO4J_URI = "your_neo4j_uri"
NEO4J_USERNAME = "your_neo4j_username"
NEO4J_PASSWORD = "your_neo4j_password"

# Zep API key
ZEP_API_KEY = "your_zep_api_key"
```

> **IMPORTANT**: Never commit your actual API keys or credentials to the repository. The `.env` files and `.streamlit/secrets.toml` are included in `.gitignore` to prevent accidental exposure of sensitive information.

## Running the Application

To run the Streamlit application:

```bash
streamlit run app.py
```

This will start the Streamlit server and open the application in your default web browser.

## Project Structure

- `app.py`: Main Streamlit application
- `agent.py`: Agent implementation using LangChain
- `graph.py`: Neo4j graph connection
- `llm.py`: Language model configuration
- `utils.py`: Utility functions
- `prompts.py`: System prompts for the agent
- `tools/`: Specialized tools for the agent
  - `cypher.py`: Tool for Cypher queries to Neo4j
  - `vector.py`: Tool for vector search of game summaries
- `data/`: Data files and scripts
  - `create_embeddings.py`: Script to create embeddings for game summaries
  - `upload_embeddings.py`: Script to upload embeddings to Neo4j
  - `neo4j_ingestion.py`: Script to ingest data into Neo4j
  - Various CSV files with 49ers data

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
   - "Who is the most popular player among fans?"

The application will use the appropriate tools to answer your questions based on the data in the Neo4j database.
