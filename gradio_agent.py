"""
Agent implementation for 49ers chatbot using LangChain and Neo4j.
Gradio-compatible version that doesn't rely on Streamlit.
"""
import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.tools import Tool
from langchain_community.chat_message_histories import ZepCloudChatMessageHistory
from langchain_community.memory.zep_cloud_memory import ZepCloudMemory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_neo4j import Neo4jChatMessageHistory
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferMemory

# Import Gradio-specific modules directly
from gradio_llm import llm
from gradio_graph import graph
from prompts import AGENT_SYSTEM_PROMPT, CHAT_SYSTEM_PROMPT
from gradio_utils import get_session_id

# Import tools
from tools.cypher import cypher_qa_wrapper
from tools.vector import get_game_summary
from tools.game_recap import game_recap_qa, get_last_game_data
from tools.player_search import player_search_qa, get_last_player_data
from tools.team_story import team_story_qa, get_last_team_story_data

# Create a basic chat chain for general football discussion
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", CHAT_SYSTEM_PROMPT),
        ("human", "{input}"),
    ]
)

# Create a non-streaming LLM for the agent
from langchain_openai import ChatOpenAI

# Import Zep client
from zep_cloud.client import Zep

# Get API key from environment only (no Streamlit)
def get_api_key(key_name):
    """Get API key from environment variables only (no Streamlit)"""
    value = os.environ.get(key_name)
    if value:
        print(f"Found {key_name} in environment variables")
    return value

OPENAI_API_KEY = get_api_key("OPENAI_API_KEY")
OPENAI_MODEL = get_api_key("OPENAI_MODEL") or "gpt-4-turbo"

# Use a fallback key if available for development
if not OPENAI_API_KEY:
    fallback_key = os.environ.get("OPENAI_API_KEY_FALLBACK")
    if fallback_key:
        print("Using fallback API key for development")
        OPENAI_API_KEY = fallback_key
    else:
        raise ValueError(f"OPENAI_API_KEY not found in environment variables")


agent_llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model=OPENAI_MODEL,
    temperature=0.1,
    streaming=True,  # Enable streaming for agent
)

movie_chat = chat_prompt | llm | StrOutputParser()

def football_chat_wrapper(input_text):
    """Wrapper function for football chat with error handling"""
    try:
        return {"output": movie_chat.invoke({"input": input_text})}
    except Exception as e:
        print(f"Error in football_chat: {str(e)}")
        return {"output": "I apologize, but I encountered an error while processing your question. Could you please rephrase it?"}

# Define the tools
tools = [
    Tool.from_function(
        name="49ers Graph Search",
        description="""Use for broader 49ers-related queries about GROUPS of players (e.g., list by position), general team info, schedules, fan chapters, or when other specific tools (like Player Search or Game Recap) are not applicable or fail.
Examples: "Who are the 49ers playing next week?", "Which players are defensive linemen?", "How many fan chapters are in California?", "List the running backs".
This is your general fallback for 49ers data if a more specific tool isn't a better fit.""",
        func=cypher_qa_wrapper
    ),
    Tool.from_function(
        name="Player Information Search",
        description="""Use this tool FIRST for any questions about a SPECIFIC player identified by name or jersey number.
Use it to get player details, stats, headshots, social media links, or an info card.
Examples: "Tell me about Brock Purdy", "Who is player number 97?", "Show me Nick Bosa's info card", "Get Deebo Samuel's stats", "Does Kalia Davis have an Instagram?"
Returns text summary and potentially visual card data.""",
        func=player_search_qa
    ),
    Tool.from_function(
        name="Team News Search",
        description="""Use for questions about recent 49ers news, articles, summaries, or specific topics like 'draft' or 'roster moves'. 
Examples: 'What's the latest team news?', 'Summarize recent articles about the draft', 'Any news about the offensive line?'
Returns text summary and potentially structured article data.""",
        func=team_story_qa
    ),
    Tool.from_function(
        name="Game Recap",
        description="""Use SPECIFICALLY for detailed game recaps or when users want to see visual information about a particular game identified by opponent or date.
Examples: "Show me the recap of the 49ers vs Jets game", "I want to see the highlights from the last 49ers game", "What happened in the game against the Patriots?"
Returns both a text summary AND visual game data that can be displayed to the user.
PREFER this tool over Game Summary Search or Graph Search for specific game detail requests.""",
        func=game_recap_qa
    ),
    Tool.from_function(
        name="Game Summary Search",
        description="""ONLY use for detailed game summaries or specific match results if the 'Game Recap' tool fails or doesn't provide enough detail.
Examples: "Summarize the 49ers vs Seahawks game", "Give me details about the last playoff game results"
Do NOT use for general schedule questions.""",
        func=get_game_summary,
    ),
    Tool.from_function(
        name="General Football Chat",
        description="""ONLY use for general football discussion NOT specific to the 49ers team, players, or games.
Examples: "How does the NFL draft work?", "What are the basic rules of football?"
Do NOT use for any 49ers-specific questions.""",
        func=football_chat_wrapper,
    )
]

# Global variables are declared before functions that use them
# This creates clarity about shared state and follows the pattern:
# "declare shared state first, then define functions that interact with it"
# Change from constant to variable with default value
memory_session_id = "241b3478c7634492abee9f178b5341cb"  # Default to Casual Fan
current_persona = "Casual Fan"  # Track the persona name for debugging

def set_memory_session_id(new_session_id, persona_name):
    """Update the global memory_session_id variable when persona changes"""
    global memory_session_id, current_persona
    memory_session_id = new_session_id
    current_persona = persona_name
    print(f"[PERSONA CHANGE] Switched to {persona_name} persona with session ID: {new_session_id}")
    return f"Persona switched to {persona_name}"

# Create the memory manager
def get_memory(session_id):
    """Get the chat history from Zep for the given session"""
    return ZepCloudChatMessageHistory(
        session_id=memory_session_id,
        api_key=os.environ.get("ZEP_API_KEY")
        # No memory_type parameter
    )

# New function to generate persona-specific instructions
def get_persona_instructions():
    """Generate personalized instructions based on current persona"""
    if current_persona == "Casual Fan":
        return """
PERSONA DIRECTIVE: CASUAL FAN MODE - YOU MUST FOLLOW THESE RULES

YOU MUST speak to a casual 49ers fan with surface-level knowledge. This means you MUST:
1. Keep explanations BRIEF and under 3-4 sentences whenever possible
2. Use EVERYDAY LANGUAGE instead of technical football terms
3. EMPHASIZE exciting plays, scoring, and player personalities
4. FOCUS on "big moments" and "highlight-reel plays" in your examples
5. AVOID detailed strategic analysis or technical football concepts
6. CREATE a feeling of inclusion by using "we" and "our team" language
7. INCLUDE at least one exclamation point in longer responses to convey excitement!

Casual fans don't know or care about: blocking schemes, defensive alignments, or salary cap details.
Casual fans DO care about: star players, touchdowns, big hits, and feeling connected to the team.

EXAMPLE RESPONSE FOR CASUAL FAN (about the draft):
"The 49ers did a great job finding exciting new players in the draft! They picked up a speedy receiver who could make some highlight-reel plays for us next season. The team focused on adding talent that can make an immediate impact, which is exactly what we needed!"
"""
    elif current_persona == "Super Fan":
        return """
PERSONA DIRECTIVE: SUPER FAN MODE - YOU MUST FOLLOW THESE RULES

YOU MUST speak to a die-hard 49ers super fan with detailed football knowledge. This means you MUST:
1. Provide DETAILED analysis that goes beyond surface-level information
2. Use SPECIFIC football terminology and scheme concepts confidently
3. REFERENCE role players and their contributions, not just star players
4. ANALYZE strategic elements of plays, drafts, and team construction
5. COMPARE current scenarios to historical team contexts when relevant
6. INCLUDE specific stats, metrics, or technical details in your analysis
7. ACKNOWLEDGE the complexity of football decisions rather than simplifying

Super fans expect: scheme-specific analysis, salary cap implications, and detailed player evaluations.
Super fans value: strategic insights, historical context, and acknowledgment of role players.

EXAMPLE RESPONSE FOR SUPER FAN (about the draft):
"The 49ers' draft strategy reflected their commitment to Shanahan's outside zone running scheme while addressing defensive depth issues. Their 3rd round selection provides versatility in the secondary with potential for both slot corner and safety roles, similar to how they've historically valued positional flexibility. The late-round offensive line selections show a continuing emphasis on athletic linemen who excel in zone blocking rather than power schemes, though they'll need development in pass protection techniques to become three-down players."
"""
    else:
        # Default case - should not happen, but provides a fallback
        return ""

# Create the agent prompt
agent_prompt = PromptTemplate.from_template(AGENT_SYSTEM_PROMPT)

# Create the agent with non-streaming LLM
agent = create_react_agent(agent_llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5  # Limit the number of iterations to prevent infinite loops
)

# Create a chat agent with memory
chat_agent = RunnableWithMessageHistory(
    agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# Create a function to initialize memory with Zep history
def initialize_memory_from_zep(session_id):
    """Initialize a LangChain memory object with history from Zep"""
    try:
        # Get history from Zep using the global session ID, not the parameter
        zep = Zep(api_key=os.environ.get("ZEP_API_KEY"))
        # Use global memory_session_id instead of the parameter
        print(f"[MEMORY LOAD] Attempting to get memory for {current_persona} persona (ID: {memory_session_id})")
        memory = zep.memory.get(session_id=memory_session_id)
        
        # Create a conversation memory with the history
        conversation_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        if memory and memory.messages:
            print(f"[MEMORY LOAD] Loading {len(memory.messages)} messages from Zep for {current_persona} persona")
            
            # Add messages to the conversation memory
            for msg in memory.messages:
                if msg.role_type == "user":
                    conversation_memory.chat_memory.add_user_message(msg.content)
                elif msg.role_type == "assistant":
                    conversation_memory.chat_memory.add_ai_message(msg.content)
            
            print("[MEMORY LOAD] Successfully loaded message history from Zep")
        else:
            print("[MEMORY LOAD] No message history found in Zep, starting fresh")
            
        return conversation_memory
    except Exception as e:
        print(f"[ERROR] Error loading history from Zep: {e}")
        # Return empty memory if there's an error
        return ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

def generate_response(user_input, session_id=None):
    """
    Generate a response using the agent and tools
    
    Args:
        user_input (str): The user's message
        session_id (str, optional): The session ID for memory
        
    Returns:
        dict: The full response object from the agent
    """
    print('[RESPONSE GEN] Starting generate_response function...')
    print(f'[RESPONSE GEN] User input: {user_input}')
    print(f'[RESPONSE GEN] Session ID: {session_id}')
    print(f'[RESPONSE GEN] Current persona: {current_persona}')

    if not session_id:
        session_id = get_session_id()
        print(f'[RESPONSE GEN] Generated new session ID: {session_id}')
    
    # Initialize memory with Zep history
    memory = initialize_memory_from_zep(session_id)
    
    # DEBUG: Print conversation memory content
    print(f"[DEBUG MEMORY] Memory type: {type(memory)}")
    if hasattr(memory, 'chat_memory') and hasattr(memory.chat_memory, 'messages'):
        print(f"[DEBUG MEMORY] Number of messages: {len(memory.chat_memory.messages)}")
        for idx, msg in enumerate(memory.chat_memory.messages):
            print(f"[DEBUG MEMORY] Message {idx}: {msg.type} - {msg.content[:100]}...")
    
    # Get persona-specific instructions for the prompt
    persona_instructions = get_persona_instructions()
    print(f'[RESPONSE GEN] Using persona instructions for: {current_persona}')
    
    # DEBUG: Print the persona instructions being used
    print(f"[DEBUG INSTRUCTIONS] Persona instructions:\n{persona_instructions}")
    
    # Create a personalized prompt by modifying the template with the current persona instructions
    # Keep the original prompt format but insert the persona instructions at the appropriate place
    persona_tag = f"[ACTIVE PERSONA: {current_persona}]"
    highlighted_instructions = f"{persona_tag}\n\n{persona_instructions}\n\n{persona_tag}"
    agent_system_prompt_with_persona = AGENT_SYSTEM_PROMPT.replace(
        "{persona_instructions}", highlighted_instructions
    )
    personalized_prompt = PromptTemplate.from_template(agent_system_prompt_with_persona)
    
    # Create a personalized agent with the updated prompt
    personalized_agent = create_react_agent(agent_llm, tools, personalized_prompt)
    
    # Create an agent executor with memory for this session and personalized prompt
    session_agent_executor = AgentExecutor(
        agent=personalized_agent,
        tools=tools,
        verbose=True,
        memory=memory,  # Use the memory we initialized
        handle_parsing_errors=True,
        max_iterations=5
    )
    
    # Add retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print('Invoking session agent executor...')
            # The agent will now have access to the loaded history
            persona_prefix = f"[RESPOND AS {current_persona.upper()}]: "
            augmented_input = f"{persona_prefix}{user_input}"
            response = session_agent_executor.invoke({"input": augmented_input})
            
            # Extract the output and format it for Streamlit
            if isinstance(response, dict):
                print('Response is a dictionary, extracting fields...')
                output = response.get('output', '')
                intermediate_steps = response.get('intermediate_steps', [])
                print(f'Extracted output: {output}')
                print(f'Extracted intermediate steps: {intermediate_steps}')
                
                # Create a formatted response
                formatted_response = {
                    "output": output,
                    "intermediate_steps": intermediate_steps,
                    "metadata": {
                        "tools_used": [step[0].tool for step in intermediate_steps] if intermediate_steps else ["None"]
                    }
                }
                print(f'Formatted response: {formatted_response}')
                return formatted_response
            else:
                print('Response is not a dictionary, converting to string...')
                return {
                    "output": str(response),
                    "intermediate_steps": [],
                    "metadata": {"tools_used": ["None"]}
                }
            
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                print(f"Error in generate_response after {max_retries} attempts: {str(e)}")
                return {
                    "output": "I apologize, but I encountered an error while processing your request. Could you please try again?",
                    "intermediate_steps": [],
                    "metadata": {"tools_used": ["None"]}
                }
            print(f"Attempt {attempt + 1} failed, retrying...")
            continue 