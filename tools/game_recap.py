"""
Game Recap - LangChain tool for retrieving and generating game recaps

This module provides functions to:
1. Search for games in Neo4j based on natural language queries
2. Generate game recaps from the structured data
3. Return both text summaries and data for UI components
"""

# Import Gradio-specific modules directly
import sys
import os
# Add parent directory to path to access gradio modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gradio_llm import llm
from gradio_graph import graph
from langchain_neo4j import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

# Create a global variable to store the last retrieved game data
# This is a workaround for LangChain dropping structured data
LAST_GAME_DATA = None

# Function to get the cached game data
def get_last_game_data():
    global LAST_GAME_DATA
    return LAST_GAME_DATA

# Function to set the cached game data
def set_last_game_data(game_data):
    global LAST_GAME_DATA
    LAST_GAME_DATA = game_data
    print(f"STORED GAME DATA IN CACHE: {game_data}")

# Create the Cypher generation prompt for game search
GAME_SEARCH_TEMPLATE = """
You are an expert Neo4j Developer translating user questions about NFL games into Cypher queries.
Your goal is to find a specific game in the database based on the user's description.

Convert the user's question based on the schema.

IMPORTANT NOTES:
1. Always return the FULL game node with ALL its properties.
2. Always use case-insensitive comparisons in your Cypher queries by applying toLower() to both the property and the search string.
3. If the question mentions a specific date, look for games on that date.
4. If the question mentions teams, look for games where those teams played.
5. If the question uses phrases like "last game", "most recent game", etc., you should add an ORDER BY clause.
6. NEVER use the embedding property in your queries.
7. ALWAYS include "g.game_id, g.date, g.location, g.home_team, g.away_team, g.result, g.summary, g.home_team_logo_url, g.away_team_logo_url, g.highlight_video_url" in your RETURN statement.

Example Questions and Queries:

1. "Tell me about the 49ers game against the Jets"
```
MATCH (g:Game)
WHERE (toLower(g.home_team) CONTAINS toLower("49ers") AND toLower(g.away_team) CONTAINS toLower("Jets"))
OR (toLower(g.away_team) CONTAINS toLower("49ers") AND toLower(g.home_team) CONTAINS toLower("Jets"))
RETURN g.game_id, g.date, g.location, g.home_team, g.away_team, g.result, g.summary, 
       g.home_team_logo_url, g.away_team_logo_url, g.highlight_video_url
```

2. "What happened in the 49ers game on October 9th?"
```
MATCH (g:Game)
WHERE (toLower(g.home_team) CONTAINS toLower("49ers") OR toLower(g.away_team) CONTAINS toLower("49ers"))
AND toLower(g.date) CONTAINS toLower("10/09")
RETURN g.game_id, g.date, g.location, g.home_team, g.away_team, g.result, g.summary, 
       g.home_team_logo_url, g.away_team_logo_url, g.highlight_video_url
```

3. "Show me the most recent 49ers game"
```
MATCH (g:Game)
WHERE (toLower(g.home_team) CONTAINS toLower("49ers") OR toLower(g.away_team) CONTAINS toLower("49ers"))
RETURN g.game_id, g.date, g.location, g.home_team, g.away_team, g.result, g.summary, 
       g.home_team_logo_url, g.away_team_logo_url, g.highlight_video_url
ORDER BY g.date DESC
LIMIT 1
```

Schema:
{schema}

Question:
{question}
"""

game_search_prompt = PromptTemplate.from_template(GAME_SEARCH_TEMPLATE)

# Create the game recap generation prompt
GAME_RECAP_TEMPLATE = """
You are a professional sports commentator for the NFL. Write an engaging and informative recap of the game described below.

Game Details:
- Date: {date}
- Location: {location}
- Home Team: {home_team}
- Away Team: {away_team}
- Final Score: {result}
- Summary: {summary}

Instructions:
1. Begin with an attention-grabbing opening that mentions both teams and the outcome.
2. Include key moments from the summary if available.
3. Mention the venue/location.
4. Conclude with what this means for the teams going forward.
5. Keep the tone professional and engaging - like an ESPN or NFL Network broadcast.
6. Write 2-3 paragraphs maximum.
7. If the 49ers are one of the teams, focus slightly more on their perspective.

Write your recap:
"""

recap_prompt = PromptTemplate.from_template(GAME_RECAP_TEMPLATE)

# Create the Cypher QA chain for game search
game_search = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    verbose=True,
    cypher_prompt=game_search_prompt,
    return_direct=True,  # Return the raw results instead of passing through LLM
    allow_dangerous_requests=True  # Required to enable Cypher queries
)

# Function to parse game data from Cypher result
def parse_game_data(result):
    """Parse the game data from the Cypher result into a structured format."""
    if not result or not isinstance(result, list) or len(result) == 0:
        return None
    
    game = result[0]
    
    # Extract home and away teams to determine winner
    home_team = game.get('g.home_team', '')
    away_team = game.get('g.away_team', '')
    result_str = game.get('g.result', 'N/A')
    
    # Parse the score if available
    home_score = away_score = 'N/A'
    winner = None
    
    if result_str and result_str != 'N/A':
        try:
            scores = result_str.split('-')
            if len(scores) == 2:
                home_score = scores[0].strip()
                away_score = scores[1].strip()
                
                # Determine winner
                home_score_int = int(home_score)
                away_score_int = int(away_score)
                winner = 'home' if home_score_int > away_score_int else 'away'
        except (ValueError, IndexError):
            pass
    
    # Build the structured game data
    game_data = {
        'game_id': game.get('g.game_id', ''),
        'date': game.get('g.date', ''),
        'location': game.get('g.location', ''),
        'home_team': home_team,
        'away_team': away_team,
        'home_score': home_score,
        'away_score': away_score,
        'result': result_str,
        'winner': winner,
        'summary': game.get('g.summary', ''),
        'home_team_logo_url': game.get('g.home_team_logo_url', ''),
        'away_team_logo_url': game.get('g.away_team_logo_url', ''),
        'highlight_video_url': game.get('g.highlight_video_url', '')
    }
    
    return game_data

# Function to generate a game recap using LLM
def generate_game_recap(game_data):
    """Generate a natural language recap of the game using the LLM."""
    if not game_data:
        return "I couldn't find information about that game."
    
    # Format the prompt with game data
    formatted_prompt = recap_prompt.format(
        date=game_data.get('date', 'N/A'),
        location=game_data.get('location', 'N/A'),
        home_team=game_data.get('home_team', 'N/A'),
        away_team=game_data.get('away_team', 'N/A'),
        result=game_data.get('result', 'N/A'),
        summary=game_data.get('summary', 'N/A')
    )
    
    # Generate the recap using the LLM
    recap = llm.invoke(formatted_prompt)
    
    return recap.content if hasattr(recap, 'content') else str(recap)

# Main function to search for a game and generate a recap
def game_recap_qa(input_text):
    """
    Search for a game based on the input text and generate a recap.
    
    Args:
        input_text (str): Natural language query about a game
        
    Returns:
        dict: Response containing text recap and structured game data
    """
    try:
        # Log the incoming query
        print(f"Processing game recap query: {input_text}")
        
        # Search for the game
        search_result = game_search.invoke({"query": input_text})
        
        # Check if we have a result
        if not search_result or not search_result.get('result'):
            return {
                "output": "I couldn't find information about that game. Could you provide more details?",
                "game_data": None
            }
        
        # Parse the game data
        game_data = parse_game_data(search_result.get('result'))
        
        if not game_data:
            return {
                "output": "I found information about the game, but couldn't process it correctly.",
                "game_data": None
            }
        
        # Generate the recap
        recap_text = generate_game_recap(game_data)
        
        # CRITICAL: Store the game data in our cache so it can be retrieved later
        # This is a workaround for LangChain dropping structured data
        set_last_game_data(game_data)
        
        # Return both the text and structured data
        return {
            "output": recap_text,
            "game_data": game_data
        }
        
    except Exception as e:
        print(f"Error in game_recap_qa: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "output": "I encountered an error while searching for the game. Please try again with a different query.",
            "game_data": None
        } 