import os
import uuid
import asyncio
import gradio as gr
from zep_cloud.client import AsyncZep
from zep_cloud.types import Message

# Import our components
# We need to modify the agent import to use our Gradio-compatible modules
# But we can't modify agent.py directly, so we'll import it and patch it
import agent
from gradio_graph import graph
import gradio_utils

# Patch the agent module to use our Gradio-compatible modules
import sys
import importlib
sys.modules['graph'] = importlib.import_module('gradio_graph')
sys.modules['llm'] = importlib.import_module('gradio_llm')

# Now we can safely import generate_response
from agent import generate_response

# Initialize Zep client
zep_api_key = os.environ.get("ZEP_API_KEY")
if not zep_api_key:
    print("ZEP_API_KEY environment variable is not set. Memory features will be disabled.")
    zep = None
else:
    zep = AsyncZep(api_key=zep_api_key)

# Global state management (replacing Streamlit's session_state)
class AppState:
    def __init__(self):
        self.messages = []
        self.initialized = False
        self.user_id = None
        self.session_id = None

# Create a global state instance
state = AppState()

# Add welcome message to state
welcome_message = """
# 🏈 Welcome to the 49ers FanAI Hub! 
        
I can help you with:
- Information about the 49ers, players, and fans
- Finding 49ers games based on plot descriptions or themes
- Discovering connections between people in the 49ers industry

What would you like to know about today?
"""

# Function to initialize the chat session
async def initialize_chat():
    """Set up the chat session when a user connects"""
    try:
        # Generate unique identifiers for the user and session
        state.user_id = gradio_utils.get_user_id()
        state.session_id = gradio_utils.get_session_id()
        
        print(f"Starting new chat session. User ID: {state.user_id}, Session ID: {state.session_id}")
        
        # Register user in Zep if available
        if zep:
            await zep.user.add(
                user_id=state.user_id,
                email="user@example.com",
                first_name="User",
                last_name="MovieFan",
            )
            
            # Start a new session in Zep
            await zep.memory.add_session(
                session_id=state.session_id,
                user_id=state.user_id,
            )
        
        
        state.messages.append({"role": "assistant", "content": welcome_message})
        state.initialized = True
        
        return welcome_message
        
    except Exception as e:
        import traceback
        print(f"Error in initialize_chat: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        error_message = "There was an error starting the chat. Please refresh the page and try again."
        state.messages.append({"role": "system", "content": error_message})
        return error_message

# Function to process user messages
async def process_message(message):
    """Process user messages and generate responses with the agent"""
    print("Starting message processing...")
    
    try:
        # Store user message in Zep memory if available
        if zep:
            print("Storing user message in Zep...")
            await zep.memory.add(
                session_id=state.session_id,
                messages=[Message(role_type="user", content=message, role="user")]
            )
        
        # Add user message to state
        state.messages.append({"role": "user", "content": message})
        
        # Process with the agent
        print('Calling generate_response function...')
        agent_response = generate_response(message, state.session_id)
        print(f"Agent response received: {agent_response}")
            
        # Extract the output and metadata
        output = agent_response.get("output", "")
        metadata = agent_response.get("metadata", {})
        print(f"Extracted output: {output}")
        print(f"Extracted metadata: {metadata}")
        
        # Add assistant response to state
        state.messages.append({"role": "assistant", "content": output})
        
        # Store assistant's response in Zep memory if available
        if zep:
            print("Storing assistant response in Zep...")
            await zep.memory.add(
                session_id=state.session_id,
                messages=[Message(role_type="assistant", content=output, role="assistant")]
            )
            print("Assistant response stored in Zep")
        
        return output
        
    except Exception as e:
        import traceback
        print(f"Error in process_message: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        error_message = "I apologize, but I encountered an error. Could you please try again?"
        state.messages.append({"role": "assistant", "content": error_message})
        return error_message

# Function to handle user input in Gradio
def user_input(message, history):
    """Handle user input and update chat history"""
    # Return immediately to update the UI with user message
    history.append({"role": "user", "content": message})
    return "", history

# Function to generate bot response in Gradio
def bot_response(history):
    """Generate bot response and update chat history"""
    # Get the last user message
    user_message = history[-1]["content"]
    
    # Process the message using asyncio.run
    response = asyncio.run(process_message(user_message))
    
    # Add the assistant's response to history
    history.append({"role": "assistant", "content": response})
    
    return history

# Function to initialize the chat when the app starts
#async def on_app_start():
    """Initialize the chat when the app starts"""
    #if not state.initialized:
    #    welcome_message = await initialize_chat()
    #    return [{"role": "assistant", "content": welcome_message}]
    #return []

# Initialize the chat before creating the interface
#initial_messages = asyncio.run(on_app_start())
initial_messages = [{"role": "assistant", "content": welcome_message}]

# Create the Gradio interface
with gr.Blocks(title="49ers FanAI Hub", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🏈 49ers FanAI Hub")
    
    # Chat interface
    chatbot = gr.Chatbot(
        value=initial_messages,
        height=500,
        show_label=False,
        elem_id="chatbot",
        type="messages"  # Use the new messages format
    )
    
    # Input components
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Ask me about the 49ers...",
            show_label=False,
            scale=9
        )
        submit = gr.Button("Send", scale=1)
    
    # Define a combined function for user input and bot response
    async def process_and_respond(message, history):
        # If not initialized yet, do it now
        if not state.initialized:
            welcome_message = await initialize_chat()
            # Optionally show the welcome message right away
            history.append({"role": "assistant", "content": welcome_message})

        # Now handle the actual user message
        history.append({"role": "user", "content": message})
        response = await process_message(message)
        history.append({"role": "assistant", "content": response})

        return "", history


    
    # Set up event handlers with the combined function - explicitly disable queue
    msg.submit(process_and_respond, [msg, chatbot], [msg, chatbot], queue=False)
    submit.click(process_and_respond, [msg, chatbot], [msg, chatbot], queue=False)
    
    # Add a clear button
    clear = gr.Button("Clear Conversation")
    clear.click(lambda: [], None, chatbot, queue=False)

# Launch the app
if __name__ == "__main__":
    # Disable the queue completely
    #demo.queue(enabled=False)
    demo.launch(share=True) 
