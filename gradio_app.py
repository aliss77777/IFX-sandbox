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
        
        # Always extract the output first, before any other processing
        output = agent_response.get("output", "")
        metadata = agent_response.get("metadata", {})
        print(f"Extracted output: {output}")
        print(f"Extracted metadata: {metadata}")
        
        # Import the game_recap module to access the cached game data
        from tools.game_recap import get_last_game_data
        
        # FIRST CHECK: Get the cached game data (this is the most reliable indicator)
        cached_game_data = get_last_game_data()
        
        # SECOND CHECK: Look for game-related keywords in the output
        is_game_related = any(keyword in output.lower() for keyword in [
            "score", "stadium", "defeated", "won", "lost", "final score",
            "game at", "home team", "away team", "dolphins", "49ers", "seahawks", 
            "jets", "vikings", "cardinals", "buccaneers", "final"
        ])
        
        # THIRD CHECK: Check metadata for Game Recap tool usage (rarely works but try)
        tools_used = metadata.get("tools_used", [])
        tool_used_game_recap = "Game Recap" in str(tools_used)
        
        # Determine if this is a game recap response
        is_game_recap = cached_game_data is not None or (is_game_related and "game" in message.lower())
        
        print(f"Is game recap detection: cached_data={cached_game_data is not None}, keywords={is_game_related}, tool={tool_used_game_recap}")
        
        if is_game_recap:
            print("Game Recap detected in response")
            
            if cached_game_data:
                print(f"Found cached game data: {cached_game_data}")
                state.set_current_game(cached_game_data)
                print("Set current game from cache")
            else:
                # Fallback for cases where the cache doesn't work
                print("No cached game data found - using text-based game detection")
                
                # Text-based game detection as a fallback
                if "Vikings" in output and "49ers" in output:
                    # Create Vikings game data
                    game_data = {
                        'game_id': 'vikings-game',
                        'date': '15/09/2024',
                        'location': 'U.S. Bank Stadium',
                        'home_team': 'Minnesota Vikings',
                        'away_team': 'San Francisco 49ers',
                        'home_score': '23',
                        'away_score': '17',
                        'result': '23-17',
                        'winner': 'home',
                        'home_team_logo_url': 'https://a.espncdn.com/i/teamlogos/nfl/500/min.png',
                        'away_team_logo_url': 'https://a.espncdn.com/i/teamlogos/nfl/500/sf.png',
                        'highlight_video_url': 'https://www.youtube.com/watch?v=jTJw2uf-Pdg'
                    }
                    state.set_current_game(game_data)
                    print("Set current game to Vikings game from text")
                elif "Dolphins" in output and "49ers" in output:
                    # Create Dolphins game data 
                    game_data = {
                        'game_id': 'dolphins-game',
                        'date': '22/12/2024',
                        'location': 'Hard Rock Stadium',
                        'home_team': 'Miami Dolphins',
                        'away_team': 'San Francisco 49ers',
                        'home_score': '29',
                        'away_score': '17',
                        'result': '29-17',
                        'winner': 'home',
                        'home_team_logo_url': 'https://a.espncdn.com/i/teamlogos/nfl/500/mia.png',
                        'away_team_logo_url': 'https://a.espncdn.com/i/teamlogos/nfl/500/sf.png',
                        'highlight_video_url': 'https://www.youtube.com/watch?v=example'
                    }
                    state.set_current_game(game_data)
                    print("Set current game to Dolphins game from text")
                else:
                    # No game detected
                    state.set_current_game(None)
                    print("No game detected in text")
        else:
            # Not a game recap query
            state.set_current_game(None)
            print("Not a game recap query")
        
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
    
    # Game recap container at the top that appears only when needed
    with gr.Row(visible=False) as game_recap_container:
        game_recap = gr.HTML()
    
    # Chat interface
    chatbot = gr.Chatbot(
        value=state.get_chat_history(),
        height=500,
        show_label=False,
        elem_id="chatbot",
        type="messages",
        render_markdown=True
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
        
        # Process the message
        response = await process_message(message)
        
        # Add text response to history
        history.append({"role": "assistant", "content": response})
        
        # Check if we have game data to display
        if state.current_game:
            # Use the create_game_recap_component function to get proper HTML
            game_data = state.current_game
            game_recap_html = create_game_recap_component(state.current_game)
            
            # Show the game recap container with the HTML content
            return "", history, game_recap_html, gr.update(visible=True)
        else:
            # Hide the game recap container
            return "", history, gr.HTML(""), gr.update(visible=False)
    
    # Set up event handlers with the combined function
    msg.submit(process_and_respond, [msg, chatbot], [msg, chatbot, game_recap, game_recap_container])
    submit.click(process_and_respond, [msg, chatbot], [msg, chatbot, game_recap, game_recap_container])
    
    # Add a clear button
    clear = gr.Button("Clear Conversation")
    
    # Clear function
    def clear_chat():
        state.set_current_game(None)
        return [], gr.HTML(""), gr.update(visible=False)
    
    clear.click(clear_chat, None, [chatbot, game_recap, game_recap_container])

# Launch the app
if __name__ == "__main__":
    demo.launch(share=True) 
