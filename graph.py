"""
This module initializes the Neo4j graph connection using Streamlit secrets.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

# Load environment variables
load_dotenv()

# Get Neo4j credentials from environment or Streamlit secrets
def get_credential(key_name):
    """Get credential from environment or Streamlit secrets"""
    # First try to get from Streamlit secrets
    if hasattr(st, 'secrets') and key_name in st.secrets:
        return st.secrets[key_name]
    # Then try to get from environment
    return os.environ.get(key_name)

# Get Neo4j credentials
AURA_CONNECTION_URI = get_credential("AURA_CONNECTION_URI") or get_credential("NEO4J_URI")
AURA_USERNAME = get_credential("AURA_USERNAME") or get_credential("NEO4J_USERNAME")
AURA_PASSWORD = get_credential("AURA_PASSWORD") or get_credential("NEO4J_PASSWORD")

# Check if credentials are available
if not all([AURA_CONNECTION_URI, AURA_USERNAME, AURA_PASSWORD]):
    missing = []
    if not AURA_CONNECTION_URI:
        missing.append("AURA_CONNECTION_URI/NEO4J_URI")
    if not AURA_USERNAME:
        missing.append("AURA_USERNAME/NEO4J_USERNAME")
    if not AURA_PASSWORD:
        missing.append("AURA_PASSWORD/NEO4J_PASSWORD")
    
    error_message = f"Missing Neo4j credentials: {', '.join(missing)}"
    st.error(error_message)
    raise ValueError(error_message)

# Connect to Neo4j
try:
    graph = Neo4jGraph(
        url=AURA_CONNECTION_URI,
        username=AURA_USERNAME,
        password=AURA_PASSWORD,
    )
except Exception as e:
    error_message = f"Failed to connect to Neo4j: {str(e)}"
    st.error(error_message)
    raise Exception(error_message)
