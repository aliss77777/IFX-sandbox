"""
This module initializes the language model and embedding model using Streamlit secrets.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load environment variables
load_dotenv()

# Get API keys from environment or Streamlit secrets
def get_api_key(key_name):
    """Get API key from environment or Streamlit secrets"""
    # First try to get from Streamlit secrets
    if hasattr(st, 'secrets') and key_name in st.secrets:
        return st.secrets[key_name]
    # Then try to get from environment
    return os.environ.get(key_name)

OPENAI_API_KEY = get_api_key("OPENAI_API_KEY")
OPENAI_MODEL = get_api_key("OPENAI_MODEL") or "gpt-4-turbo"

if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY is not set in environment variables or Streamlit secrets.")
    raise ValueError("OPENAI_API_KEY is not set")

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
except Exception as e:
    st.error(f"Failed to initialize OpenAI models: {str(e)}")
    raise Exception(f"Failed to initialize OpenAI models: {str(e)}")
