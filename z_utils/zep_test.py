"""
Simple Zep test script to retrieve chat history from a pre-defined session.
This follows step 2 of Task 1.3 Memory & Persona Implementation.
"""
import os
import json
import argparse
from dotenv import load_dotenv
from zep_cloud.client import Zep
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables from .env file
load_dotenv()

# Get Zep API key
ZEP_API_KEY = os.environ.get("ZEP_API_KEY")
if not ZEP_API_KEY:
    raise RuntimeError("ZEP_API_KEY missing in environment variables.")

# Initialize Zep client
zep = Zep(api_key=ZEP_API_KEY)

def retrieve_chat_history(session_id):
    """
    Retrieve chat history for a specific session from Zep.
    
    Args:
        session_id (str): The session ID to retrieve history for
        
    Returns:
        dict: The memory object containing context and messages
    """
    try:
        # Use Zep's memory.get API to retrieve chat history
        memory = zep.memory.get(session_id=session_id)
        return memory
    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        return None

def get_zep_history(session_id):
    """
    Retrieve chat history directly from Zep using the client.
    
    Args:
        session_id (str): The session ID to retrieve history for
        
    Returns:
        list: Formatted messages for LangChain
    """
    try:
        zep = Zep(api_key=os.environ.get("ZEP_API_KEY"))
        memory = zep.memory.get(session_id=session_id)
        
        # Convert Zep messages to LangChain format
        formatted_messages = []
        if memory and memory.messages:
            for msg in memory.messages:
                if msg.role_type == "user":
                    formatted_messages.append(HumanMessage(content=msg.content))
                elif msg.role_type == "assistant":
                    formatted_messages.append(AIMessage(content=msg.content))
        
        return formatted_messages
    except Exception as e:
        print(f"Error retrieving Zep history: {e}")
        return []

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Retrieve chat history from Zep')
    parser.add_argument('--session_id', type=str, 
                        default="241b3478c7634492abee9f178b5341cb",
                        help='Session ID to retrieve (default: Casual Fan)')
    args = parser.parse_args()
    
    session_id = args.session_id
    
    print(f"Retrieving chat history for session ID: {session_id}")
    
    # Get the memory for the session
    memory = retrieve_chat_history(session_id)
    
    if memory:
        print("\n===== MEMORY CONTEXT =====")
        print(memory.context)
        
        print("\n===== CHAT MESSAGES =====")
        for msg in memory.messages:
            print(f"{msg.role_type} ({msg.role}): {msg.content}")
        
        print("\nSuccessfully retrieved chat history!")
    else:
        print("Failed to retrieve chat history.")

if __name__ == "__main__":
    main() 