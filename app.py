 
import os
import uuid
import streamlit as st
from zep_cloud.client import AsyncZep
from zep_cloud.types import Message
import asyncio

# Import our components
from agent import generate_response
from utils import get_session_id, get_user_id, write_message
from graph import graph

# Page configuration
st.set_page_config(
    page_title="49ers FanAI Hub",
    page_icon="🏈",
    layout="wide"
)

# Initialize Zep client
zep_api_key = os.environ.get("ZEP_API_KEY")
if not zep_api_key:
    st.error("ZEP_API_KEY environment variable is not set. Please set it to use memory features.")
    zep = None
else:
    zep = AsyncZep(api_key=zep_api_key)

# Initialize session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "initialized" not in st.session_state:
    st.session_state.initialized = False

# Function to initialize the chat session
async def initialize_chat():
    """Set up the chat session when a user connects"""
    try:
        # Generate unique identifiers for the user and session
        user_id = get_user_id()
        session_id = get_session_id()
        
        print(f"Starting new chat session. User ID: {user_id}, Session ID: {session_id}")
        
        # Register user in Zep if available
        if zep:
            await zep.user.add(
                user_id=user_id,
                email="user@example.com",
                first_name="User",
                last_name="MovieFan",
            )
            
            # Start a new session in Zep
            await zep.memory.add_session(
                session_id=session_id,
                user_id=user_id,
            )
        
        # Add welcome message to session state
        welcome_message = """
# 🏈 Welcome to the 49ers FanAI Hub! 
        
I can help you with:
- Information about the 49ers, players, and fans
- Finding 49ers games based on plot descriptions or themes
- Discovering connections between people in the 49ers industry

What would you like to know about today?
"""
        st.session_state.messages.append({"role": "assistant", "content": welcome_message})
        st.session_state.initialized = True
        
    except Exception as e:
        import traceback
        print(f"Error in initialize_chat: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        st.session_state.messages.append({
            "role": "system",
            "content": "There was an error starting the chat. Please refresh the page and try again."
        })

# Function to process user messages
async def process_message(message):
    """Process user messages and generate responses with the agent"""
    print("Starting message processing...")
    session_id = get_session_id()
    print(f"Session ID: {session_id}")
    
    try:
        # Store user message in Zep memory if available
        if zep:
            print("Storing user message in Zep...")
            await zep.memory.add(
                session_id=session_id,
                messages=[Message(role_type="user", content=message, role="user")]
            )
        
        # Process with the agent
        print('Calling generate_response function...')
        agent_response = generate_response(message, session_id)
        print(f"Agent response received: {agent_response}")
            
        # Extract the output and metadata
        output = agent_response.get("output", "")
        metadata = agent_response.get("metadata", {})
        print(f"Extracted output: {output}")
        print(f"Extracted metadata: {metadata}")
        
        # Add assistant response to session state
        st.session_state.messages.append({"role": "assistant", "content": output})
        
        # Store assistant's response in Zep memory if available
        if zep:
            print("Storing assistant response in Zep...")
            await zep.memory.add(
                session_id=session_id,
                messages=[Message(role_type="assistant", content=output, role="assistant")]
            )
            print("Assistant response stored in Zep")
        
    except Exception as e:
        import traceback
        print(f"Error in process_message: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "I apologize, but I encountered an error. Could you please try again?"
        })

# Initialize the chat session if not already initialized
if not st.session_state.initialized:
    asyncio.run(initialize_chat())

# Display chat messages
for message in st.session_state.messages:
    write_message(message["role"], message["content"], save=False)

# Chat input
if prompt := st.chat_input("Ask me about the 49ers..."):
    # Display user message and save to history
    write_message("user", prompt)
    
    # Process the message and display response
    with st.spinner("Thinking..."):
        # Process the message asynchronously
        asyncio.run(process_message(prompt))
        
        # Force a rerun to display the new message
        st.rerun()
