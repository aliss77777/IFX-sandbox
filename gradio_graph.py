"""
This module initializes the Neo4j graph connection without Streamlit dependencies.
"""

import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

# Load environment variables
load_dotenv()

# Get Neo4j credentials from environment
def get_credential(key_name):
    """Get credential from environment variables"""
    # Try different possible environment variable names
    possible_names = [key_name]
    
    # Add alternative names
    if key_name.startswith("AURA_"):
        possible_names.append(f"NEO4J_{key_name[5:]}")
    elif key_name.startswith("NEO4J_"):
        possible_names.append(f"AURA_{key_name[6:]}")
    
    # Try each possible name
    for name in possible_names:
        value = os.environ.get(name)
        if value:
            return value
    
    return None

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
    print(f"ERROR: {error_message}")
    raise ValueError(error_message)

# Connect to Neo4j
try:
    graph = Neo4jGraph(
        url=AURA_CONNECTION_URI,
        username=AURA_USERNAME,
        password=AURA_PASSWORD,
    )
    print("Successfully connected to Neo4j database")
except Exception as e:
    error_message = f"Failed to connect to Neo4j: {str(e)}"
    print(f"ERROR: {error_message}")
    raise Exception(error_message)
