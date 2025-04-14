import os
import uuid
import asyncio
import gradio as gr
from zep_cloud.client import AsyncZep
from zep_cloud.types import Message

# Import our components
import agent
from gradio_graph import graph
import gradio_utils
from components.game_recap_component import create_game_recap_component

# Patch the agent module to use our Gradio-compatible modules
import sys
import importlib
sys.modules['graph'] = importlib.import_module('gradio_graph')
sys.modules['llm'] = importlib.import_module('gradio_llm')

# Now we can safely import generate_response
from agent import generate_response

# Define CSS directly
css = """
/* Base styles */
body {
    font-family: 'Arial', sans-serif;
    background-color: #111111;
    color: #E6E6E6;
}

/* Headings */
h1, h2, h3 {
    color: #AA0000;
}

/* Buttons */
button {
    background-color: #AA0000;
    color: #FFFFFF;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
}

button:hover {
    background-color: #B3995D;
}

/* Game Recap Component */
.game-recap-container {
    background-color: #111111;
    padding: 20px;
    margin: 20px 0;
    border-radius: 10px;
}

.game-recap-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 20px 0;
}

.team-info {
    text-align: center;
}

.team-logo {
    width: 100px;
    height: 100px;
    margin-bottom: 10px;
}

.team-name {
    font-size: 1.2em;
    color: #E6E6E6;
}

.team-score {
    font-size: 2em;
    color: #FFFFFF;
    font-weight: bold;
}

.winner {
    color: #B3995D;
}

.video-preview {
    background-color: #222222;
    padding: 15px;
    border-radius: 5px;
    margin-top: 20px;
}

/* Chat Interface */
.chatbot {
    background-color: #111111;
    border: 1px solid #333333;
    border-radius: 10px;
    padding: 20px;
    margin: 20px 0;
}

.message-input {
    background-color: #222222;
    color: #E6E6E6;
    border: 1px solid #333333;
    border-radius: 5px;
    padding: 10px;
}

.clear-button {
    background-color: #AA0000;
    color: #FFFFFF;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    margin-top: 10px;
}

.clear-button:hover {
    background-color: #B3995D;
}
"""

# Initialize Zep client
zep_api_key = os.environ.get("ZEP_API_KEY")
if not zep_api_key:
    print("ZEP_API_KEY environment variable is not set. Memory features will be disabled.")
    zep = None
else:
    zep = AsyncZep(api_key=zep_api_key)

class AppState:
    def __init__(self):
        self.chat_history = []
        self.current_game = None
        self.initialized = False
        self.user_id = None
        self.session_id = None
        self.zep_client = None

    def add_message(self, role, content):
        self.chat_history.append({"role": role, "content": content})

    def get_chat_history(self):
        return self.chat_history

    def set_current_game(self, game_data):
        self.current_game = game_data

# Initialize global state
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

# Initialize the chat session
async def initialize_chat():
    """Initialize the chat session with Zep and return a welcome message."""
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
        
        # Add welcome message to state
        state.add_message("assistant", welcome_message)
        state.initialized = True
        
        return welcome_message
        
    except Exception as e:
        import traceback
        print(f"Error in initialize_chat: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        error_message = "There was an error starting the chat. Please refresh the page and try again."
        state.add_message("system", error_message)
        return error_message

# Process a message and return a response
async def process_message(message):
    """Process a message and return a response."""
    try:
        # Store user message in Zep memory if available
        if zep:
            print("Storing user message in Zep...")
            await zep.memory.add(
                session_id=state.session_id,
                messages=[Message(role_type="user", content=message, role="user")]
            )
        
        # Add user message to state
        state.add_message("user", message)
        
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
        state.add_message("assistant", output)
        
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
        state.add_message("assistant", error_message)
        return error_message

# Function to handle user input in Gradio
def user_input(message, history):
    """Handle user input and update the chat history."""
    # Check if this is the first message (initialization)
    if not state.initialized:
        # Initialize the chat session
        asyncio.run(initialize_chat())
        state.initialized = True
    
    # Add the user message to the history
    history.append({"role": "user", "content": message})
    
    # Clear the input field
    return "", history

# Function to generate bot response in Gradio
def bot_response(history):
    """Generate a response from the bot and update the chat history."""
    # Get the last user message
    user_message = history[-1]["content"]
    
    # Process the message and get a response
    response = asyncio.run(process_message(user_message))
    
    # Add the bot response to the history
    history.append({"role": "assistant", "content": response})
    
    return history

# Create the Gradio interface
with gr.Blocks(title="49ers FanAI Hub", theme=gr.themes.Soft(), css=css) as demo:
    gr.Markdown("# 🏈 49ers FanAI Hub")
    
    # Game Recap Component
    with gr.Row():
        game_recap = create_game_recap_component(state.current_game)
    
    # Chat interface
    chatbot = gr.Chatbot(
        value=state.get_chat_history(),
        height=500,
        show_label=False,
        elem_id="chatbot",
        type="messages"
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
    demo.launch(share=True) 
