import os
import uuid
import asyncio
import gradio as gr
from zep_cloud.client import AsyncZep
from zep_cloud.types import Message

# Import the Gradio-specific implementations directly, not patching
from gradio_graph import graph
from gradio_llm import llm
import gradio_utils
from components.game_recap_component import create_game_recap_component
from components.player_card_component import create_player_card_component
from components.team_story_component import create_team_story_component

# Import the Gradio-compatible agent instead of the original agent
import gradio_agent
from gradio_agent import generate_response

# Import cache getter functions
from tools.game_recap import get_last_game_data
from tools.player_search import get_last_player_data
from tools.team_story import get_last_team_story_data

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
        self.initialized = False
        self.user_id = None
        self.session_id = None
        self.zep_client = None

    def add_message(self, role, content):
        self.chat_history.append({"role": role, "content": content})

    def get_chat_history(self):
        return self.chat_history

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
    """Process a message and return a response (text only)."""
    # NOTE: This function now primarily focuses on getting the agent's text response.
    # UI component updates are handled in process_and_respond based on cached data.
    try:
        # Store user message in Zep memory if available
        if zep:
            print("Storing user message in Zep...")
            await zep.memory.add(
                session_id=state.session_id,
                messages=[Message(role_type="user", content=message, role="user")]
            )

        # Add user message to state (for context, though Gradio manages history display)
        # state.add_message("user", message)

        # Process with the agent
        print('Calling generate_response function...')
        agent_response = generate_response(message, state.session_id)
        print(f"Agent response received: {agent_response}")

        # Always extract the text output
        output = agent_response.get("output", "I apologize, I encountered an issue.")
        # metadata = agent_response.get("metadata", {})
        print(f"Extracted output: {output}")

        # Add assistant response to state (for context)
        # state.add_message("assistant", output)

        # Store assistant's response in Zep memory if available
        if zep:
            print("Storing assistant response in Zep...")
            await zep.memory.add(
                session_id=state.session_id,
                messages=[Message(role_type="assistant", content=output, role="assistant")]
            )
            print("Assistant response stored in Zep")

        return output # Return only the text output

    except Exception as e:
        import traceback
        print(f"Error in process_message: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        error_message = f"I'm sorry, there was an error processing your request: {str(e)}"
        # state.add_message("assistant", error_message)
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

    # --- Component Display Area --- #
    # REMOVED Unused/Redundant Component Placeholders:
    # debug_textbox = gr.Textbox(label="Debug Player Data", visible=True, interactive=False)
    # player_card_display = gr.HTML(visible=False)
    # game_recap_display = gr.HTML(visible=False)

    # Chat interface - Components will be added directly here
    chatbot = gr.Chatbot(
        # value=state.get_chat_history(), # Let Gradio manage history display directly
        height=500,
        show_label=False,
        elem_id="chatbot",
        # type="messages", # Using default tuple format as components are added
        render_markdown=True
    )

    # Input components
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Ask me about the 49ers...",
            show_label=False,
            scale=9
        )
        submit_btn = gr.Button("Send", scale=1) # Renamed for clarity

    # Define a combined function for user input and bot response
    async def process_and_respond(message, history):
        """Process user input, get agent response, check for components, and update history."""
        
        print(f"process_and_respond: Received message: {message}")
        # history.append((message, None)) # Add user message placeholder
        # yield "", history # Show user message immediately

        # Call the agent to get the response (text output + potentially populates cached data)
        agent_response = generate_response(message, state.session_id)
        text_output = agent_response.get("output", "Sorry, something went wrong.")
        metadata = agent_response.get("metadata", {})
        tools_used = metadata.get("tools_used", ["None"])
        
        print(f"process_and_respond: Agent text output: {text_output}")
        print(f"process_and_respond: Tools used: {tools_used}")

        # Initialize response list with the text output
        response_list = [(message, text_output)]

        # Check for specific component data based on tools used or cached data
        # Important: Call the getter functions *after* generate_response has run
        
        # Check for Player Card
        player_data = get_last_player_data()
        if player_data:
            print(f"process_and_respond: Found player data: {player_data}")
            player_card_component = create_player_card_component(player_data)
            if player_card_component:
                response_list.append((None, player_card_component))
                print("process_and_respond: Added player card component.")
            else:
                 print("process_and_respond: Player data found but component creation failed.")

        # Check for Game Recap
        game_data = get_last_game_data()
        if game_data:
            print(f"process_and_respond: Found game data: {game_data}")
            game_recap_comp = create_game_recap_component(game_data)
            if game_recap_comp:
                response_list.append((None, game_recap_comp))
                print("process_and_respond: Added game recap component.")
            else:
                 print("process_and_respond: Game data found but component creation failed.")

        # Check for Team Story --- NEW --- 
        team_story_data = get_last_team_story_data()
        if team_story_data:
             print(f"process_and_respond: Found team story data: {team_story_data}")
             team_story_comp = create_team_story_component(team_story_data)
             if team_story_comp:
                  response_list.append((None, team_story_comp))
                  print("process_and_respond: Added team story component.")
             else:
                  print("process_and_respond: Team story data found but component creation failed.")
                 
        # Update history with all parts of the response (text + components)
        # Gradio's Chatbot handles lists of (user, assistant) tuples, 
        # where assistant can be text or a Gradio component.
        # We replace the last entry (user, None) with the actual response items.
        
        # Gradio manages history display; we just return the latest exchange.
        # The actual history state is managed elsewhere (e.g., Zep, Neo4j history)
        
        # Return the combined response list to update the chatbot UI
        # The first element is user message + assistant text response
        # Subsequent elements are None + UI component
        print(f"process_and_respond: Final response list for UI: {response_list}")
        # Return values suitable for outputs: [msg, chatbot]
        return "", response_list # Return empty string for msg, list for chatbot

    # Set up event handlers with the combined function
    # Ensure outputs list matches the return values of process_and_respond
    # REMOVED redundant components from outputs_list
    outputs_list = [msg, chatbot]
    msg.submit(process_and_respond, [msg, chatbot], outputs_list)
    submit_btn.click(process_and_respond, [msg, chatbot], outputs_list)

    # Add a clear button
    clear_btn = gr.Button("Clear Conversation")

    # Clear function - now only needs to clear msg and chatbot
    def clear_chat():
        # Return empty values for msg and chatbot
        return "", [] 

    # Update clear outputs - only need msg and chatbot
    clear_btn.click(clear_chat, None, [msg, chatbot])

# Launch the app
if __name__ == "__main__":
    demo.launch(share=True) 
