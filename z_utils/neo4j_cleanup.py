#!/usr/bin/env python
"""
Script to perform Neo4j cleanup: Remove the 'embedding' property from all :Game nodes.
This is part of Task 1.3 housekeeping.

Run once: python ifx-sandbox/z_utils/neo4j_cleanup.py
"""

import os
import sys

# Adjust path to import graph object from the parent directory (ifx-sandbox)
# Assumes script is run from the workspace root directory
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ifx_sandbox_path = os.path.join(workspace_root, 'ifx-sandbox')

if ifx_sandbox_path not in sys.path:
    print(f"Adding {ifx_sandbox_path} to sys.path")
    sys.path.insert(0, ifx_sandbox_path)

try:
    # Import the configured graph instance from ifx-sandbox directory
    from gradio_graph import graph 
    print("Successfully imported graph object from gradio_graph.")
except ImportError as e:
    print(f"Error importing gradio_graph: {e}")
    print("Please ensure gradio_graph.py exists in the 'ifx-sandbox' directory and is configured correctly.")
    print("Make sure you are running this script from the workspace root directory.")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during import: {e}")
    sys.exit(1)

def cleanup_game_embeddings():
    """Removes the embedding property from all Game nodes in Neo4j."""
    print("Starting Neo4j cleanup: Removing 'embedding' property from :Game nodes...")
    
    cleanup_query = """
    MATCH (g:Game)
    WHERE g.embedding IS NOT NULL
    REMOVE g.embedding
    RETURN count(g) as removed_count
    """
    
    try:
        result = graph.query(cleanup_query)
        
        if result and isinstance(result, list) and len(result) > 0 and 'removed_count' in result[0]:
            count = result[0]['removed_count']
            print(f"Successfully removed 'embedding' property from {count} :Game node(s).")
        else:
            # Query might return empty list if no nodes matched or had the property
            print("Cleanup query executed. No 'embedding' properties found or removed from :Game nodes (or query result format unexpected).")
            print(f"Raw query result: {result}")
            
    except Exception as e:
        print(f"Error executing Neo4j cleanup query: {e}")
        print("Cleanup failed.")

if __name__ == "__main__":
    print("Running Neo4j Game Embedding Cleanup script...")
    # Basic check: Does 'ifx-sandbox' exist relative to script location?
    if not os.path.isdir(ifx_sandbox_path):
         print("Error: Cannot find 'ifx-sandbox' directory.")
         print("Please ensure you run this script from the workspace root directory.")
         sys.exit(1)
         
    cleanup_game_embeddings()
    print("Script execution complete.") 