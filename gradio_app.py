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
from components.game_recap_component import create_game_recap_component, process_game_recap_response

# Import the Gradio-compatible agent instead of the original agent
import gradio_agent
from gradio_agent import generate_response

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
        print(f"Updated current game: {game_data}")

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
        
        # Check if game recap is mentioned in the output and no direct metadata info
        if "game" in message.lower() and "49ers" in output and any(team in output for team in ["Jets", "Buccaneers", "Seahawks"]):
            print("Game content detected in response")
            
            # Hardcoded game detection - simple but effective
            if "Jets" in output and "32-19" in output:
                # Jets game data
                game_data = {
                    'game_id': 'jets-game',
                    'date': '10/9/24',
                    'location': "Levi's Stadium",
                    'home_team': 'San Francisco 49ers',
                    'away_team': 'New York Jets',
                    'home_score': '32',
                    'away_score': '19',
                    'result': '32-19',
                    'winner': 'home',
                    'home_team_logo_url': 'https://a.espncdn.com/i/teamlogos/nfl/500/sf.png',
                    'away_team_logo_url': 'https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png',
                    'highlight_video_url': 'https://www.youtube.com/watch?v=igOb4mfV7To'
                }
                state.set_current_game(game_data)
                print(f"Set current game to Jets game")
            
            elif "Buccaneers" in output and "23-20" in output:
                # Bucs game data
                game_data = {
                    'game_id': 'bucs-game',
                    'date': '10/11/24',
                    'location': 'Raymond James Stadium',
                    'home_team': 'Tampa Bay Buccaneers',
                    'away_team': 'San Francisco 49ers',
                    'home_score': '20',
                    'away_score': '23',
                    'result': '20-23',
                    'winner': 'away',
                    'home_team_logo_url': 'https://a.espncdn.com/i/teamlogos/nfl/500/tb.png',
                    'away_team_logo_url': 'https://a.espncdn.com/i/teamlogos/nfl/500/sf.png',
                    'highlight_video_url': 'https://www.youtube.com/watch?v=607mv01G8UU'
                }
                state.set_current_game(game_data)
                print(f"Set current game to Bucs game")
            else:
                # No specific game recognized
                state.set_current_game(None)
        else:
            # Not a game recap query
            state.set_current_game(None)
        
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
        error_message = f"I'm sorry, there was an error processing your request: {str(e)}"
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
    
    # Game Recap Component (use a container with HTML inside)
    with gr.Column(visible=False) as game_recap_container:
        game_recap = gr.HTML("")
    
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
        
        # Update game recap component visibility based on current_game
        has_game_data = state.current_game is not None
        
        # Create the game recap HTML content if we have game data
        if has_game_data:
            # Pass the HTML component directly
            game_recap_html = create_game_recap_component(state.current_game)
            # Use gr.update() for the container visibility
            container_update = gr.update(visible=True)
        else:
            # Create an empty HTML component
            game_recap_html = gr.HTML("")
            # Use gr.update() to hide the container
            container_update = gr.update(visible=False)
        
        # Return in order: msg (empty), history, game_recap HTML component, container visibility update
        return "", history, game_recap_html, container_update
    
    # Set up event handlers with the combined function - explicitly disable queue
    msg.submit(process_and_respond, [msg, chatbot], [msg, chatbot, game_recap, game_recap_container], queue=False)
    submit.click(process_and_respond, [msg, chatbot], [msg, chatbot, game_recap, game_recap_container], queue=False)
    
    # Add a clear button
    clear = gr.Button("Clear Conversation")
    
    # Clear function that also hides the game recap
    def clear_chat():
        state.set_current_game(None)
        return [], gr.HTML(""), gr.update(visible=False)
    
    clear.click(clear_chat, None, [chatbot, game_recap, game_recap_container], queue=False)

# Launch the app
if __name__ == "__main__":
    demo.launch(share=True) 
