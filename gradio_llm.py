"""
This module initializes the language model and embedding model without Streamlit dependencies.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load environment variables from the ifx-sandbox/.env file
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(PROJECT_DIR, ".env")
load_dotenv(ENV_FILE)
print(f"Loading environment variables from: {ENV_FILE}")

# Get API keys from environment
def get_api_key(key_name):
    """Get API key from environment variables only, no Streamlit"""
    value = os.environ.get(key_name)
    if value:
        print(f"Found {key_name} in environment variables")
    else:
        print(f"WARNING: {key_name} not found in environment variables")
    return value

OPENAI_API_KEY = get_api_key("OPENAI_API_KEY")
OPENAI_MODEL = get_api_key("OPENAI_MODEL") or "gpt-4-turbo"

if not OPENAI_API_KEY:
    error_message = "OPENAI_API_KEY is not set in environment variables."
    print(f"ERROR: {error_message}")
    # Use a fallback API key for development testing, if available
    fallback_key = os.environ.get("OPENAI_API_KEY_FALLBACK")
    if fallback_key:
        print("Using fallback API key for development")
        OPENAI_API_KEY = fallback_key
    else:
        raise ValueError(error_message)

# Create the LLM with better error handling
try:
    llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model=OPENAI_MODEL,
        temperature=0.1,
        streaming=True  # Enable streaming for better response handling
    )

    # Create the Embedding model
    embeddings = OpenAIEmbeddings(
        openai_api_key=OPENAI_API_KEY
    )
    
    print(f"Successfully initialized OpenAI models (using {OPENAI_MODEL})")
except Exception as e:
    error_message = f"Failed to initialize OpenAI models: {str(e)}"
    print(f"ERROR: {error_message}")
    raise Exception(error_message)
