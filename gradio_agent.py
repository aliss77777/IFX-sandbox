"""
Agent implementation for 49ers chatbot using LangChain and Neo4j.
Gradio-compatible version that doesn't rely on Streamlit.
"""
import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.tools import Tool
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_neo4j import Neo4jChatMessageHistory
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

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
    streaming=True  # Enable streaming for agent
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

# Create the memory manager
def get_memory(session_id):
    """Get the chat history from Neo4j for the given session"""
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)

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

def generate_response(user_input, session_id=None):
    """
    Generate a response using the agent and tools
    
    Args:
        user_input (str): The user's message
        session_id (str, optional): The session ID for memory
        
    Returns:
        dict: The full response object from the agent
    """
    print('Starting generate_response function...')
    print(f'User input: {user_input}')
    print(f'Session ID: {session_id}')

    if not session_id:
        session_id = get_session_id()
        print(f'Generated new session ID: {session_id}')
        
    # Add retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print('Invoking chat_agent...')
            response = chat_agent.invoke(
                {"input": user_input},
                {"configurable": {"session_id": session_id}},
            )
            print(f'Raw response from chat_agent: {response}')
            
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